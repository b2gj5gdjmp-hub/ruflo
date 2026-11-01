# Builds teil-01/index.html as a 2D cartoon (SVG characters) from shot specs, voice segments and lip-sync envelopes.
import json, sys, wave, random
import numpy as np
sys.path.insert(0, "tools")
from chars import character, DEFS, C
from scenes import SCENES, WALL, table, counter

V = json.load(open("voice/segments.json"))
G = json.load(open("tools/groups.json"))
SPEAKER = {sid: line[0] for g in G.values() for sid, line in zip(g["ids"], g["lines"])}
DEFAULT = {"Leo": 0, "Mia": 312, "Chantal": 48, "Henri": 1250, "Karl": 3}

# framing: head centre to screen y, scale
F = {"CU": (2.25, 760), "MCU": (1.55, 640), "MED": (1.15, 600), "WIDE": (0.7, None), "XCU": (5.4, None),
     "SCU": (2.05, 820), "SMED": (1.05, 820)}


def place(name, frame, x):
    s, hy_screen = F[frame]
    hy = C[name]["hy"]
    if frame == "WIDE": return x, 1720, s
    if frame == "XCU": return x, 900 - (hy - 100) * s, s   # display centre near y 900
    return x, hy_screen - hy * s, s


def ch(n, f, x, pose="down", expr="neutral", gaze=(0, 0), disp=None, move=None, seated=False):
    return dict(n=n, f=f, x=x, pose=pose, expr=expr, gaze=gaze, disp=disp, move=move, seated=seated)


SHOTS = [
    ("01", "A", False, [ch("Leo", "MED", 540, "point", "smirk", (0, 0), [[0, 2400000]])], None),
    ("02", "A", True, [ch("Leo", "CU", 540, "down", "smirk", (.6, 0), [[0, 2400000]])], None),
    ("03", "A", False, [ch("Henri", "MED", 560, "down", "worried", (-.7, 0))], None),
    ("04", "A", True, [ch("Leo", "CU", 540, "head", "smirk", (0, -.3), [[0, 2400000], [1.0, 0]])], None),
    ("05", "B", False, [ch("Leo", "WIDE", 250, "down", "smile", (1, 0), move=(140, 0)), ch("Chantal", "WIDE", 820, "down", "smirk", (-1, 0))], None),
    ("06", "B", True, [ch("Chantal", "CU", 540, "down", "disgust", (-.5, 0))], None),
    ("07", "B", True, [ch("Leo", "CU", 540, "open", "surprised", (.6, 0))], None),
    ("08", "B", True, [ch("Chantal", "CU", 540, "crossed", "angry", (-.3, 0))], None),
    ("09", "B", False, [ch("Leo", "MED", 330, "down", "neutral", (1, 0)), ch("Chantal", "MED", 860, "down", "angry", (1, 0), move=(520, .3))], None),
    ("10", "B", False, [ch("Leo", "MCU", 230, "down", "smile", (1, 0)), ch("Mia", "MCU", 790, "down", "smile", (-1, 0))], None),
    ("11", "B", True, [ch("Mia", "CU", 540, "down", "smile", (-.5, 0))], None),
    ("12", "B", True, [ch("Leo", "CU", 540, "open", "smile", (.6, 0))], None),
    ("13", "B", True, [ch("Mia", "CU", 540, "crossed", "smirk", (-.5, 0))], None),
    ("14", "B", True, [ch("Leo", "CU", 540, "down", "wink", (.4, 0))], None),
    ("15", "C", False, [ch("Leo", "SMED", 190, "down", "smile", (1, -.3), seated=True), ch("Mia", "SMED", 890, "down", "smile", (-1, -.3), seated=True),
                        ch("Karl", "MED", 540, "notepad", "smile", (0, .2))], ("table", 1270, ("water", "candle", "water"))),
    ("16", "C", True, [ch("Mia", "SCU", 540, "down", "smile", (.5, -.2), seated=True)], ("table", 1610, ("water",))),
    ("17", "C", True, [ch("Leo", "SCU", 540, "down", "smile", (-.5, 0), seated=True)], ("table", 1610, ("water",))),
    ("18", "C", False, [ch("Leo", "SMED", 300, "down", "neutral", (1, 0), seated=True), ch("Mia", "SMED", 770, "down", "sad", (-1, 0), seated=True)], ("table", 1270, ("water", "candle", "water"))),
    ("19", "C", False, [ch("Leo", "MED", 540, "down", "neutral", (.6, 0))], ("table", 1240, ("candle",))),
    ("20", "D", False, [ch("Leo", "MCU", 300, "lips", "smirk", (1, 0)), ch("Karl", "MCU", 800, "notepad", "neutral", (-1, 0))], ("counter", 1560)),
    ("21", "D", True, [ch("Karl", "CU", 540, "notepad", "surprised", (-.4, 0))], ("counter", 1800)),
    ("22", "D", True, [ch("Leo", "CU", 540, "lips", "wink", (.3, 0))], ("counter", 1830)),
    ("23", "E", False, [ch("Mia", "SMED", 800, "down", "surprised", (-1, -.2), seated=True), ch("Karl", "MED", 300, "tray", "smile", (1, .3))], ("table", 1270, ("lobster", "champagne", "champagne"))),
    ("24", "E", True, [ch("Mia", "SCU", 540, "both", "surprised", (0, .3), seated=True)], ("table", 1610, ("champagne",))),
    ("25", "E", True, [ch("Mia", "SCU", 540, "head", "think", (.7, -.3), seated=True)], None),
    ("26", "E", True, [ch("Mia", "XCU", 540, "down", "think", (.7, -.3), [[0, 312], [.45, 7800000, 1], [1.8, 312, 1]])], None),
    ("27", "E", True, [ch("Leo", "CU", 540, "down", "worried", (.5, 0))], None),
    ("28", "E", True, [ch("Mia", "SCU", 540, "down", "forced", (-.3, 0), seated=True)], ("table", 1610, ("champagne",))),
]
SHOT_META = {s["id"]: s for s in json.load(open("tools/shots.json"))}

# ---- timing (same rules as build.py)
GAP, SCENE_GAP, LEAD = 0.22, 0.35, 0.12
t = 0.0; timing = {}; audios = []; prev = None
for sid, scene, *_ in SHOTS:
    m = SHOT_META[sid]
    if prev and scene != prev: t += SCENE_GAP - GAP
    start = t; cur = t + LEAD
    for lid in m["lines"]:
        audios.append((lid, round(cur, 3), V[lid]["dur"], sid)); cur += V[lid]["dur"] + GAP
    end = max(cur, start + .8) + m.get("hold", 0) if m["lines"] else start + m.get("hold", 1.5)
    timing[sid] = (round(start, 3), round(end - start, 3)); t = end; prev = scene
STING = t - .4
TOTAL = round(t + 1.9, 3)
timing['28'] = (timing['28'][0], round(TOTAL - timing['28'][0], 3))


def env(path, fps=30):
    w = wave.open(path); sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)
    hop = sr // fps; r = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a), hop)])
    r = r / (np.percentile(r, 92) + 1e-6); r = np.clip(r, 0, 1)
    r = np.convolve(r, [.25, .5, .25], "same")
    return [round(float(x), 2) for x in r]


shots_html, rig = [], {"lines": [], "disp": [], "blink": [], "bob": [], "move": []}
for k, (sid, scene, blur, cast, fg) in enumerate(SHOTS):
    st, du = timing[sid]
    chars = []
    for c in cast:
        cid = f"s{sid}{c['n']}"
        x, y, s = place(c["n"], c["f"], c["x"])
        if c["seated"] and not c["f"].startswith("S"): y += 170 * s
        vals = c["disp"] or [[0, DEFAULT[c["n"]]]]
        v0 = f"{int(vals[0][1]):,}".replace(",", ".")
        chars.append(f'<g transform="translate({x:.0f} {y:.0f}) scale({s})"><g id="{cid}-mv">{character(c["n"], cid, c["pose"], c["expr"], c["gaze"], v0, c["seated"])}</g></g>')
        if len(vals) > 1: rig["disp"].append([cid, [[st + k[0], k[1], k[2] if len(k) > 2 else 0] for k in vals]])
        rnd = random.Random(cid)
        bt = st + rnd.uniform(.4, 1.4)
        while bt < st + du - .2:
            if c["expr"] != "wink": rig["blink"].append([cid, round(bt, 3)])
            bt += rnd.uniform(2.2, 3.8)
        rig["bob"].append([cid, st, st + du, rnd.uniform(0, 6.28)])
        if c["move"]: rig["move"].append([cid, st + c["move"][1] * du, st + du, c["move"][0]])
    fgs = ""
    if fg and fg[0] == "table": fgs = table(fg[1], fg[2])
    if fg and fg[0] == "counter": fgs = counter(fg[1])
    bg = SCENES[scene]()
    bgs = f'<g filter="url(#bgblur)">{bg}</g>' if blur else bg
    sweat = '<path d="M700 640 Q722 690 700 712 Q678 690 700 640Z" fill="#9FD8FF" stroke="#fff" stroke-width="3"/>' if sid == "28" else ""
    shots_html.append(f'<div id="s{sid}" class="clip shot" data-start="{st}" data-duration="{du}" data-track-index="1" style="z-index:{k + 1}">'
                      f'<div class="cam" id="c{sid}"><svg viewBox="0 0 1080 1920" width="1080" height="1920">{bgs}{"".join(chars)}{fgs}{sweat}</svg></div></div>')
for lid, at, du, sid in audios:
    cid = f"s{sid}{SPEAKER[lid]}"
    rig["lines"].append([cid, at, env(f"teil-01/assets/voice/l{lid}.wav"), .55 if lid in ("25", "22") else 1])

js_cam = []
for k, (sid, *_r) in enumerate(SHOTS):
    st, du = timing[sid]
    a, b = ["{scale:1.0}|{scale:1.06}", "{scale:1.06,x:-14}|{scale:1.06,x:14}", "{scale:1.05}|{scale:1.0}", "{scale:1.06,x:14}|{scale:1.06,x:-14}"][k % 4].split("|")
    if sid == "26": a, b = "{scale:1.0}", "{scale:1.12}"
    js_cam.append(f'tl.fromTo("#c{sid}",{a},{{...{b},duration:{du},ease:"none"}},{st});')

audio_html = [f'<audio id="a{lid}" class="clip" data-start="{at}" data-duration="{du}" data-track-index="2" src="assets/voice/l{lid}.wav"></audio>' for lid, at, du, _ in audios]
s04 = timing["04"][0]; s26 = timing["26"][0]
audio_html += [f'<audio id="fx-roll" class="clip" data-start="{s04 + 1.0}" data-duration="1.1" data-track-index="3" src="assets/sfx/roll.wav"></audio>',
               f'<audio id="fx-flicker" class="clip" data-start="{s26 + .5}" data-duration="1.1" data-track-index="3" src="assets/sfx/flicker.wav"></audio>',
               f'<audio id="fx-sting" class="clip" data-start="{round(STING, 3)}" data-duration="2.2" data-track-index="3" src="assets/sfx/sting.wav"></audio>']

html = f'''<!doctype html>
<html lang="de" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="assets/js/gsap.min.js"></script>
<style>
@font-face {{ font-family:"DSEG7"; src:url("assets/fonts/DSEG7Classic-Bold.woff2") format("woff2"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:#000; }}
#root {{ width:100%; height:100%; position:relative; overflow:hidden; background:#000; }}
.shot {{ position:absolute; inset:0; overflow:hidden; background:#000; }}
.cam {{ position:absolute; inset:0; transform-origin:50% 40%; }}
.cam svg {{ display:block; }}
#defs {{ position:absolute; width:0; height:0; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
<svg id="defs" width="0" height="0"><defs>{DEFS}{WALL}</defs></svg>
{chr(10).join(shots_html)}
{chr(10).join(audio_html)}
</div>
<script>
const RIG = {json.dumps(rig, separators=(",", ":"))};
const $ = id => document.getElementById(id);
const fmt = v => String(Math.round(v)).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, ".");
function setD(cid, v) {{
  const t = $(cid + "-dt"), e = $(cid + "-de"); if (!t) return;
  const s = fmt(v); if (t.textContent === s) return; t.textContent = s;
  const w = +t.dataset.w, n = s.replace(/\\D/g, "").length || 1;
  t.setAttribute("font-size", Math.min(w * .17, (w - 56) / (n * .86)).toFixed(1));
  const c = v >= 1000 ? "#3dff6e" : "#ff3b3b"; t.setAttribute("fill", c); e.setAttribute("fill", c);
}}
function render(T) {{
  for (const [cid, keys] of RIG.disp) {{
    let v = keys[0][1];
    for (let i = 1; i < keys.length; i++) {{
      const [t0, a] = keys[i - 1], [t1, b, jump] = keys[i], d = jump ? .001 : Math.min(.9, (t1 - t0) * .8);
      if (T >= t1 + d) v = b; else if (T >= t1) {{ const p = (T - t1) / d; v = a + (b - a) * (p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2); }}
    }}
    setD(cid, v);
    const scr = $(cid + "-scr"); const last = keys[keys.length - 1][0];
    if (scr) scr.setAttribute("opacity", keys.some(k => T > k[0] && T < k[0] + .5 && k !== keys[0] && Math.floor(T * 24) % 2) ? .35 : 1);
  }}
  const open = {{}};
  for (const [cid, t0, e, g] of RIG.lines) {{
    const i = Math.floor((T - t0) * 30);
    if (i >= 0 && i < e.length) open[cid] = Math.max(open[cid] || 0, e[i] * g);
    else if (T >= t0 - .05 && T < t0 + e.length / 30 + .05) open[cid] = open[cid] || 0;
  }}
  for (const el of document.querySelectorAll("[id$='-mt']")) {{
    const cid = el.id.slice(0, -3), a = open[cid];
    el.setAttribute("transform", `scale(1 ${{a === undefined ? .05 : (.12 + .88 * a).toFixed(2)}})`);
    $(cid + "-ms").setAttribute("opacity", a === undefined ? 1 : 0);
  }}
  const bl = {{}};
  for (const [cid, t] of RIG.blink) if (T >= t && T < t + .12) bl[cid] = 1;
  for (const [cid, a, b, ph] of RIG.bob) {{
    if (T < a - .1 || T > b + .1) continue;
    $(cid + "-bob").setAttribute("transform", `translate(0 ${{(Math.sin(T * 2.2 + ph) * 6).toFixed(2)}})`);
    const h = $(cid + "-head"); const talk = open[cid] !== undefined;
    h.setAttribute("transform", `rotate(${{(Math.sin(T * (talk ? 3.1 : 1.3) + ph) * (talk ? 2.2 : .9)).toFixed(2)}} 0 -650)`);
    for (const s of ["l", "r"]) {{ const eye = $(cid + "-eye" + s); if (eye) eye.setAttribute("transform", bl[cid] ? `translate(0 ${{eye.dataset.cy * .9}}) scale(1 .1)` : ""); }}
  }}
  for (const [cid, a, b, dx] of RIG.move) {{
    const p = Math.max(0, Math.min(1, (T - a) / (b - a)));
    $(cid + "-mv").setAttribute("transform", `translate(${{(dx * p).toFixed(1)}} 0)`);
  }}
}}
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js_cam)}
const clock = {{ t: 0 }};
tl.to(clock, {{ t: {TOTAL}, duration: {TOTAL}, ease: "none", onUpdate: () => render(clock.t) }}, 0);
window.__timelines["main"] = tl;
tl.seek(0); render(0);
</script>
</body>
</html>
'''
open("teil-01/index.html", "w").write(html)
print("total", TOTAL, "kB", len(html) // 1024)
json.dump(timing, open("tools/timing.json", "w"))
