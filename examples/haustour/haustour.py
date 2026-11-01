#!/usr/bin/env python3
"""haustour.py - cinematic house-tour videos from still photos.

Each photo gets a monocular depth map (Depth Anything V2, ONNX, CPU). The
renderer then moves a virtual 3D camera through the photo (dolly, orbit,
crane, truck) with real parallax, so foreground and background move
differently. Rooms are joined with "walk-through" transitions: the camera
accelerates forward into one room and arrives decelerating in the next.

Usage:
  python haustour.py fotos/ -o tour.mp4 --title "Villa Mare" \
      --subtitle "Mallorca · 4 Schlafzimmer · Pool" --outro "Jetzt anfragen"
  python haustour.py tour.json -o tour.mp4          # per-shot control
  python haustour.py fotos/ -o reel.mp4 --format 9:16 --music song.mp3

Folder mode: photos are used in filename order; "03_Wohnzimmer.jpg" is
labelled "Wohnzimmer". JSON mode: same CLI keys plus
  "shots": [{"image": "a.jpg", "label": "Pool", "move": "orbit-left",
             "duration": 4.5, "focus": [0.5, 0.5]}, ...]
Moves: dolly-in, dolly-out, push-orbit-left/right, orbit-left/right,
       truck-left/right, crane-up, crane-down.
Requires: ffmpeg, pip install onnxruntime opencv-python-headless numpy pillow
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

MODEL_URL = ("https://github.com/fabio-sim/Depth-Anything-ONNX/releases/"
             "download/v2.0.0/depth_anything_v2_vits.onnx")
MODEL_PATH = Path.home() / ".cache" / "haustour" / "depth_anything_v2_vits.onnx"
FONT_DIR = Path("/usr/share/fonts/opentype/inter")
FONT_BOLD = FONT_DIR / "InterDisplay-SemiBold.otf"
FONT_LIGHT = FONT_DIR / "InterDisplay-Light.otf"
FORMATS = {"16:9": (16, 9), "9:16": (9, 16), "1:1": (1, 1), "4:5": (4, 5)}
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".tif", ".tiff"}
OVERSCAN = 1.25  # source canvas is larger than the frame so moves never show edges

# Camera paths: (start, end) for tx, ty (sideways/vertical), tz (forward).
# "orbit" adds a counter-pan that keeps the focus point fixed on screen.
MOVES = {
    "dolly-in": dict(tz=(0.0, 0.22)),
    "dolly-out": dict(tz=(0.22, 0.0)),
    "push-orbit-left": dict(tx=(0.06, -0.06), tz=(0.03, 0.17), orbit=True),
    "push-orbit-right": dict(tx=(-0.06, 0.06), tz=(0.03, 0.17), orbit=True),
    "orbit-left": dict(tx=(0.09, -0.09), tz=(0.07, 0.07), orbit=True),
    "orbit-right": dict(tx=(-0.09, 0.09), tz=(0.07, 0.07), orbit=True),
    "truck-left": dict(tx=(0.07, -0.07), tz=(0.05, 0.08)),
    "truck-right": dict(tx=(-0.07, 0.07), tz=(0.05, 0.08)),
    "crane-up": dict(ty=(0.06, -0.06), tz=(0.03, 0.12), orbit=True),
    "crane-down": dict(ty=(-0.06, 0.06), tz=(0.03, 0.12), orbit=True),
}
AUTO_MOVES = ["push-orbit-right", "dolly-in", "orbit-left", "push-orbit-left",
              "truck-right", "crane-up", "orbit-right", "dolly-in"]
# Transition: which camera parameter gets the extra "travel" and how much.
TRANSITIONS = {"walk": ("tz", 0.20, 0.14), "whip": ("pan_x", 0.14, 0.14),
               "fade": (None, 0.0, 0.0)}


@dataclass
class Shot:
    image: Path
    label: str = ""
    move: str = ""
    duration: float = 4.0
    focus: tuple = (0.5, 0.5)
    rgb: np.ndarray = field(default=None, repr=False)    # float32 BGR canvas
    disp: np.ndarray = field(default=None, repr=False)   # half-res disparity
    d_focus: float = 0.5


# ----------------------------------------------------------------- depth ---
class Depth:
    def __init__(self, model: Path):
        if not model.exists():
            model.parent.mkdir(parents=True, exist_ok=True)
            print(f"Lade Tiefenmodell nach {model} ...", file=sys.stderr)
            urllib.request.urlretrieve(MODEL_URL, model)
        self.sess = ort.InferenceSession(str(model),
                                         providers=["CPUExecutionProvider"])
        self.inp = self.sess.get_inputs()[0].name

    def __call__(self, bgr: np.ndarray) -> np.ndarray:
        """Relative disparity in [0,1] (1 = near), same size as input."""
        x = cv2.resize(bgr, (518, 518), interpolation=cv2.INTER_AREA)
        x = x[:, :, ::-1].astype(np.float32) / 255.0
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        x = x.transpose(2, 0, 1)[None].astype(np.float32)
        d = self.sess.run(None, {self.inp: x})[0][0]
        d = cv2.resize(d, (bgr.shape[1], bgr.shape[0]), interpolation=cv2.INTER_CUBIC)
        lo, hi = np.percentile(d, [2, 98])
        return np.clip((d - lo) / max(hi - lo, 1e-6), 0, 1).astype(np.float32)


def prepare(shot: Shot, depth: Depth, W: int, H: int, grade: bool) -> None:
    """Load photo, cover-fit it onto the overscan canvas, compute depth."""
    im = ImageOps.exif_transpose(Image.open(shot.image)).convert("RGB")
    cw, ch = int(W * OVERSCAN), int(H * OVERSCAN)
    s = max(cw / im.width, ch / im.height)
    im = im.resize((max(cw, round(im.width * s)), max(ch, round(im.height * s))),
                   Image.LANCZOS)
    fx, fy = shot.focus
    x0 = int(np.clip(fx * im.width - cw / 2, 0, im.width - cw))
    y0 = int(np.clip(fy * im.height - ch / 2, 0, im.height - ch))
    bgr = np.asarray(im.crop((x0, y0, x0 + cw, y0 + ch)))[:, :, ::-1].copy()
    if grade:
        bgr = color_grade(bgr)
    d = depth(bgr)
    # Dilate the near layer so object edges don't smear into the background,
    # then smooth to avoid tearing.
    k = max(3, int(cw * 0.012) | 1)
    d = cv2.dilate(d, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    d = cv2.GaussianBlur(d, (0, 0), cw * 0.006)
    d = 0.15 + 0.85 * d  # disparity range: far 0.15 ... near 1.0
    shot.rgb = bgr.astype(np.float32) / 255.0
    shot.disp = cv2.resize(d, (cw // 2, ch // 2), interpolation=cv2.INTER_AREA)
    shot.d_focus = float(np.median(d[ch // 2 - ch // 8: ch // 2 + ch // 8,
                                     cw // 2 - cw // 8: cw // 2 + cw // 8]))


def color_grade(bgr: np.ndarray) -> np.ndarray:
    """Mild real-estate grade: lift shadows, gentle S-curve, +8% saturation."""
    x = bgr.astype(np.float32) / 255.0
    x = x + 0.24 * x * (1 - x) ** 2          # lift shadows
    x = x - 0.02 * np.sin(2 * np.pi * x)     # soft S-curve
    hsv = cv2.cvtColor(np.clip(x, 0, 1), cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.08, 0, 1)
    return (cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR) * 255).clip(0, 255).astype(np.uint8)


# ---------------------------------------------------------------- render ---
class Renderer:
    def __init__(self, W: int, H: int):
        self.W, self.H = W, H
        self.F = float(W)  # focal length in pixels (≈ 53° horizontal FOV)
        h2, w2 = H // 2, W // 2
        ys, xs = np.mgrid[0:h2, 0:w2].astype(np.float32)
        self.u = (xs * 2 + 1 - W / 2) / self.F   # normalised output coords
        self.v = (ys * 2 + 1 - H / 2) / self.F
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
        self.vignette = (1 - 0.22 * np.clip(r / 0.72, 0, 1) ** 2.2)[..., None]

    def view(self, shot: Shot, cam: dict) -> np.ndarray:
        """Backward-warp the photo for camera (tx, ty, tz, pan_x, pan_y)."""
        tx, ty, tz = cam.get("tx", 0), cam.get("ty", 0), cam.get("tz", 0)
        px, py = cam.get("pan_x", 0), cam.get("pan_y", 0)
        if cam.get("orbit"):
            k = 1 - tz * shot.d_focus
            px -= tx * shot.d_focus / k
            py -= ty * shot.d_focus / k
        ch, cw = shot.rgb.shape[:2]
        dh, dw = shot.disp.shape
        uo, vo = self.u + px, self.v + py
        # Fixed-point iteration: depth must be read at the *source* position.
        us, vs = uo.copy(), vo.copy()
        for _ in range(3):
            mx = (us * self.F + cw / 2) * (dw / cw)
            my = (vs * self.F + ch / 2) * (dh / ch)
            D = cv2.remap(shot.disp, mx, my, cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)
            k = np.maximum(1 - tz * D, 0.45)
            us, vs = uo * k + tx * D, vo * k + ty * D
        mx = cv2.resize(us * self.F + cw / 2, (self.W, self.H))
        my = cv2.resize(vs * self.F + ch / 2, (self.W, self.H))
        return cv2.remap(shot.rgb, mx, my, cv2.INTER_CUBIC,
                         borderMode=cv2.BORDER_REFLECT)


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def camera(shot: Shot, idx: int, n: int, t: float, T: float, trans: str) -> dict:
    """Camera state of `shot` at local time t (0..duration)."""
    mv = MOVES[shot.move]
    p = t / shot.duration
    if idx == 0:
        p = 0.5 * ease_io(p) + 0.5 * p           # soft start
    if idx == n - 1:
        p = 1 - (0.5 * ease_io(1 - p) + 0.5 * (1 - p))  # soft landing
    cam = {k: v[0] + (v[1] - v[0]) * p for k, v in mv.items() if k != "orbit"}
    cam["orbit"] = mv.get("orbit", False)
    key, out_amt, in_amt = TRANSITIONS[trans]
    # Gentle steadicam float so it never looks like a locked-off still.
    cam["pan_x"] = cam.get("pan_x", 0) + 0.0018 * math.sin(1.3 * t + idx)
    cam["pan_y"] = cam.get("pan_y", 0) + 0.0013 * math.sin(0.9 * t + 2 * idx)
    if key and T > 0:
        sign = lambda j: -1 if (key == "pan_x" and j % 2) else 1  # alternate whips
        if idx < n - 1 and t > shot.duration - T:      # accelerate out of room
            x = (t - (shot.duration - T)) / T
            cam[key] = cam.get(key, 0) + sign(idx) * out_amt * x ** 2.2
        if idx > 0 and t < T:                          # glide into next room
            x = 1 - t / T
            cam[key] = cam.get(key, 0) - sign(idx - 1) * in_amt * x ** 2.2
    return cam


# -------------------------------------------------------------- overlays ---
def _font(path: Path, size: int):
    try:
        return ImageFont.truetype(str(path), size)
    except OSError:
        return ImageFont.load_default()


def overlay(W, H, draw_fn) -> tuple:
    """Render an RGBA overlay with soft shadow; returns (bgr, alpha) floats."""
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(txt))
    a = txt.split()[3]
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(a.filter(ImageFilter.GaussianBlur(H * 0.008)).point(lambda v: v * 0.7))
    img = Image.alpha_composite(shadow, txt)
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr[:, :, 2::-1].copy(), arr[:, :, 3:4].copy()


def label_layer(W, H, text):
    s = min(W, H)
    f = _font(FONT_BOLD, int(s * 0.048))
    x, y = int(W * 0.06), int(H * (0.84 if H > W else 0.80))

    def draw(d):
        d.line([(x, y - s * 0.025), (x + s * 0.07, y - s * 0.025)],
               fill=(255, 255, 255, 230), width=max(2, int(s * 0.004)))
        d.text((x, y), text.upper(), font=f, fill=(255, 255, 255, 245))
    return overlay(W, H, draw)


def title_layer(W, H, title, subtitle):
    s = min(W, H)
    ft, fs = _font(FONT_BOLD, int(s * 0.10)), _font(FONT_LIGHT, int(s * 0.042))

    def draw(d):
        tw = d.textlength(title, font=ft)
        d.text(((W - tw) / 2, H * 0.42), title, font=ft, fill=(255, 255, 255, 255))
        if subtitle:
            sw = d.textlength(subtitle, font=fs)
            d.text(((W - sw) / 2, H * 0.42 + s * 0.14), subtitle, font=fs,
                   fill=(255, 255, 255, 235))
    return overlay(W, H, draw)


def logo_layer(W, H, path):
    lg = Image.open(path).convert("RGBA")
    lg.thumbnail((int(W * 0.16), int(H * 0.09)), Image.LANCZOS)
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    m = int(min(W, H) * 0.04)
    canvas.paste(lg, (W - lg.width - m, m), lg)
    arr = np.asarray(canvas).astype(np.float32) / 255.0
    return arr[:, :, 2::-1].copy(), arr[:, :, 3:4] * 0.88


def window(t, a, b, fade=0.45):
    if t < a or t > b:
        return 0.0
    return min(1.0, (t - a) / fade, (b - t) / fade)


def comp(frame, layer, k):
    if k > 0:
        rgb, a = layer
        a = a * k
        frame = frame * (1 - a) + rgb * a
    return frame


# ------------------------------------------------------------------ main ---
def load_job(args) -> tuple:
    src = Path(args.input)
    cfg = {}
    if src.suffix.lower() == ".json":
        cfg = json.loads(src.read_text(encoding="utf-8"))
        base = src.parent
        shots = [Shot(image=base / s["image"], label=s.get("label", ""),
                      move=s.get("move", ""), duration=float(s.get("duration", args.duration)),
                      focus=tuple(s.get("focus", (0.5, 0.5)))) for s in cfg["shots"]]
    else:
        files = sorted(p for p in src.iterdir() if p.suffix.lower() in IMG_EXT)
        shots = [Shot(image=p, label=auto_label(p), duration=args.duration) for p in files]
    if not shots:
        sys.exit("Keine Fotos gefunden.")
    for i, s in enumerate(shots):
        if not s.move:
            s.move = AUTO_MOVES[i % len(AUTO_MOVES)]
        if s.move not in MOVES:
            sys.exit(f"Unbekannte Bewegung '{s.move}'. Erlaubt: {', '.join(MOVES)}")
    for k in ("title", "subtitle", "outro", "music", "logo", "format", "transition"):
        if getattr(args, k) is None and k in cfg:
            setattr(args, k, cfg[k] if k in ("title", "subtitle", "outro", "format",
                                             "transition") else str(src.parent / cfg[k]))
    return shots


def auto_label(p: Path) -> str:
    stem = re.sub(r"^[\d\s_\-.]+", "", p.stem)
    if not stem or re.match(r"(?i)^(img|dsc|pxl|photo|image|whatsapp)", stem):
        return ""
    return re.sub(r"[_\-]+", " ", stem).strip().title()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="Ordner mit Fotos oder tour.json")
    ap.add_argument("-o", "--output", default="haustour.mp4")
    ap.add_argument("--format", default=None, choices=list(FORMATS))
    ap.add_argument("--height", type=int, default=1080, help="Kurze Seite in Pixel")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--duration", type=float, default=4.2, help="Sekunden pro Raum")
    ap.add_argument("--transition", default=None, choices=list(TRANSITIONS))
    ap.add_argument("--transition-len", type=float, default=0.9)
    ap.add_argument("--title"), ap.add_argument("--subtitle"), ap.add_argument("--outro")
    ap.add_argument("--music"), ap.add_argument("--logo")
    ap.add_argument("--no-grade", action="store_true")
    ap.add_argument("--model", type=Path, default=MODEL_PATH)
    args = ap.parse_args()

    shots = load_job(args)
    args.format = args.format or "16:9"
    args.transition = args.transition or "walk"
    a, b = FORMATS[args.format]
    short = args.height
    W, H = (round(short * a / b), short) if a >= b else (short, round(short * b / a))
    W, H = W - W % 2, H - H % 2
    fps, T, n = args.fps, args.transition_len, len(shots)

    depth = Depth(args.model)
    for i, s in enumerate(shots):
        print(f"[{i + 1}/{n}] Tiefe: {s.image.name}  ({s.move})", file=sys.stderr)
        prepare(s, depth, W, H, not args.no_grade)

    starts, t0 = [], 0.0
    for s in shots:
        starts.append(t0)
        t0 += s.duration - T
    total = t0 + T
    rend = Renderer(W, H)
    labels = [label_layer(W, H, s.label) if s.label else None for s in shots]
    title = title_layer(W, H, args.title, args.subtitle) if args.title else None
    outro = title_layer(W, H, args.outro, "") if args.outro else None
    logo = logo_layer(W, H, args.logo) if args.logo else None

    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if args.music:
        cmd += ["-stream_loop", "-1", "-i", args.music, "-map", "0:v", "-map", "1:a",
                "-af", f"afade=t=in:d=1,afade=t=out:st={total - 2.5:.2f}:d=2.5",
                "-c:a", "aac", "-b:a", "192k"]
    cmd += ["-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.output]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    nframes = int(round(total * fps))
    for f in range(nframes):
        t = f / fps
        layers = []
        for i, s in enumerate(shots):
            lt = t - starts[i]
            if 0 <= lt <= s.duration:
                layers.append((i, s, lt))
        out = None
        for i, s, lt in layers:
            in_trans = (i < n - 1 and lt > s.duration - T) or (i > 0 and lt < T)
            sub = 5 if in_trans and args.transition != "fade" else 1
            img = sum(rend.view(s, camera(s, i, n, lt + (k / sub - 0.5) * 1.6 / fps,
                                          T, args.transition)) for k in range(sub)) / sub
            if out is None:
                out = img
            else:  # crossfade concentrated around peak speed
                x = ease_io((lt / T - 0.3) / 0.4) if args.transition != "fade" else ease_io(lt / T)
                out = out * (1 - x) + img * x
        out = out * rend.vignette
        i, s, lt = layers[-1]  # newest active room owns the label
        if labels[i] is not None and not (i == 0 and title):
            out = comp(out, labels[i], window(lt, T * 0.9, T * 0.9 + 2.6))
        if title:
            out = comp(out, title, window(t, 0.5, min(3.8, shots[0].duration - 0.3), 0.7))
        if outro:
            k = window(t, total - 3.2, total + 1, 0.7)
            out = out * (1 - 0.35 * k)
            out = comp(out, outro, k)
        if logo:
            out = comp(out, logo, 1.0)
        out = out * min(1.0, t / 0.5, (total - t) / 0.6)  # fade from/to black
        ff.stdin.write((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if f % fps == 0:
            print(f"\rRendern {f / nframes:5.1%}", end="", file=sys.stderr)
    ff.stdin.close()
    ff.wait()
    print(f"\rFertig: {args.output}  ({total:.1f}s, {W}x{H})", file=sys.stderr)


if __name__ == "__main__":
    main()
