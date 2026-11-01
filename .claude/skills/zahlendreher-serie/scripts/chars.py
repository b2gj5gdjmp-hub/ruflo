# SVG character rigs for @zahlendreher.tv (2D cartoon). Local coords: feet at y=0, x centred.
import random

DEFS = """
<radialGradient id="g-laugen" cx="38%" cy="28%" r="80%"><stop offset="0" stop-color="#C9783A"/><stop offset=".55" stop-color="#94481A"/><stop offset="1" stop-color="#5E2A0C"/></radialGradient>
<radialGradient id="g-baguette" cx="35%" cy="25%" r="85%"><stop offset="0" stop-color="#F6D08A"/><stop offset=".6" stop-color="#D99A48"/><stop offset="1" stop-color="#A9672A"/></radialGradient>
<radialGradient id="g-potato" cx="35%" cy="30%" r="85%"><stop offset="0" stop-color="#E4C08C"/><stop offset=".6" stop-color="#C39560"/><stop offset="1" stop-color="#8E6436"/></radialGradient>
<radialGradient id="g-skin" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#FFE0C8"/><stop offset=".7" stop-color="#F3BE98"/><stop offset="1" stop-color="#D9976F"/></radialGradient>
<linearGradient id="g-shirt-black" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#34343c"/><stop offset="1" stop-color="#141418"/></linearGradient>
<linearGradient id="g-jeans" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FB3DA"/><stop offset="1" stop-color="#5D82AE"/></linearGradient>
<linearGradient id="g-red" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E8303C"/><stop offset="1" stop-color="#9E1420"/></linearGradient>
<linearGradient id="g-cardigan" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBF7F1"/><stop offset="1" stop-color="#DCD3C6"/></linearGradient>
<radialGradient id="g-shine" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="#fff" stop-opacity=".55"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="9"/></filter>
<filter id="bgblur" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="7"/></filter>
<filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="10" stdDeviation="12" flood-color="#000" flood-opacity=".35"/></filter>
"""

C = {
    "Leo":     dict(kind="food", head="laugen", w=130, h=175, top="#2a2a30", shirt="url(#g-shirt-black)", pants="#1b1b20", shoe="#111", hand="#A85A24", sleeve="#26262c", hy=-790),
    "Henri":   dict(kind="food", head="baguette", w=105, h=230, top="#111", shirt="#15151a", pants="#121216", shoe="#0b0b0b", hand="#ffffff", sleeve="#15151a", hy=-820, bow=True, vest="#f4f4f4"),
    "Karl":    dict(kind="food", head="potato", w=135, h=150, top="#222", shirt="#f2f0ea", pants="#1d1d22", shoe="#111", hand="#C9A06A", sleeve="#f2f0ea", hy=-770, bow=True, vest="#202024"),
    "Mia":     dict(kind="human", hair="#6B3A22", hair2="#8C5232", top="#ffffff", shirt="url(#g-cardigan)", pants="url(#g-jeans)", shoe="#f4f4f4", hand="url(#g-skin)", sleeve="#EEE8DF", iris="#6B4226", hy=-760),
    "Chantal": dict(kind="human", hair="#EBC86A", hair2="#F7DE95", top="#E8303C", shirt="url(#g-red)", pants=None, shoe="#f4f4f4", hand="url(#g-skin)", sleeve=None, iris="#3E7CB1", hy=-760, dress=True),
}

# arm poses: points relative to shoulder (character's right arm = screen left when facing viewer)
ARMS = {
    "down":    ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (18, 130), (14, 245)]),
    "point":   ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (80, 40), (190, -40)]),
    "open":    ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (40, 125), (150, 95)]),
    "both":    ([(0, 0), (-40, 125), (-150, 95)], [(0, 0), (40, 125), (150, 95)]),
    "head":    ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (70, 60), (-70, -205)]),
    "lips":    ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (60, 80), (-112, -55)]),
    "crossed": ([(0, 0), (-25, 120), (175, 160)], [(0, 0), (25, 120), (-175, 175)]),
    "tray":    ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (55, 110), (170, 100)]),
    "notepad": ([(0, 0), (-30, 125), (95, 120)], [(0, 0), (30, 125), (-40, 110)]),
    "chin":    ([(0, 0), (-18, 130), (-14, 245)], [(0, 0), (40, 120), (-60, -35)]),
}

BROWS = {  # (angle_inner_raise for left, right, dy)
    "neutral": (0, 0, 0), "smile": (-4, -4, -4), "smirk": (-10, 8, 0), "worried": (18, 18, 0),
    "angry": (-20, -20, 6), "disgust": (-16, 10, 4), "surprised": (4, 4, -16), "sad": (20, 20, 4),
    "wink": (-6, -6, -2), "forced": (14, 14, -4), "think": (12, -6, 0),
}
MOUTHS = {
    "neutral": "M-26 0 Q0 6 26 0", "smile": "M-36 -6 Q0 30 36 -6", "smirk": "M-30 4 Q8 10 34 -12",
    "worried": "M-26 8 Q0 -6 26 8", "angry": "M-28 10 Q0 -4 28 10", "disgust": "M-30 6 Q-6 -8 30 10",
    "sad": "M-26 12 Q0 -6 26 12", "wink": "M-36 -6 Q0 30 36 -6", "forced": "M-38 0 L38 0", "think": "M-20 4 Q4 0 24 -6",
}


def _arm(pts, sx, sy, sleeve, hand, w, human):
    p = [(sx + x, sy + y) for x, y in pts]
    d = f"M{p[0][0]} {p[0][1]} Q{p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]}"
    sl = f'<path d="{d}" fill="none" stroke="{sleeve}" stroke-width="{w}" stroke-linecap="round"/>' if sleeve else \
         f'<path d="{d}" fill="none" stroke="url(#g-skin)" stroke-width="{w - 10}" stroke-linecap="round"/>'
    hr = 22 if human else 27
    return sl + f'<circle cx="{p[2][0]}" cy="{p[2][1]}" r="{hr}" fill="{hand}" stroke="rgba(0,0,0,.12)" stroke-width="2"/>'


def _head(c, cid, hy):
    w, h = c.get("w", 120), c.get("h", 160)
    k = c.get("head")
    if k == "laugen":
        rnd = random.Random(7)
        pts = [(rnd.uniform(-1, 1), rnd.uniform(-1, 1)) for _ in range(80)]
        pts = [(x, y) for x, y in pts if x * x + y * y < .8 and y < -.62][:16]
        salt = "".join(f'<rect x="{x * w:.0f}" y="{hy + y * h:.0f}" width="10" height="8" rx="2.5" fill="#fff" opacity=".93"/>' for x, y in pts)
        knot = f'<path d="M-50 {hy - h + 12} C-90 {hy - h - 60} -10 {hy - h - 70} 0 {hy - h - 10} C10 {hy - h - 70} 90 {hy - h - 60} 50 {hy - h + 12}" fill="none" stroke="#7A3A12" stroke-width="26" stroke-linecap="round"/>'
        return knot + f'<rect x="{-w}" y="{hy - h}" width="{2 * w}" height="{2 * h}" rx="{w}" fill="url(#g-laugen)"/>' + \
            f'<ellipse cx="{-w * .38}" cy="{hy - h * .62}" rx="{w * .32}" ry="{h * .22}" fill="url(#g-shine)"/>' + salt
    if k == "baguette":
        cuts = "".join(f'<path d="M-60 {hy - h + 40 + i * 62} Q0 {hy - h + 10 + i * 62} 60 {hy - h - 6 + i * 62}" stroke="#F8E2B0" stroke-width="12" fill="none" stroke-linecap="round" opacity=".85"/>' for i in range(3))
        return f'<rect x="{-w}" y="{hy - h}" width="{2 * w}" height="{2 * h}" rx="{w}" fill="url(#g-baguette)"/>' + cuts + \
            f'<ellipse cx="{-w * .4}" cy="{hy - h * .55}" rx="{w * .25}" ry="{h * .3}" fill="url(#g-shine)"/>'
    if k == "potato":
        spots = "".join(f'<ellipse cx="{x}" cy="{hy + y}" rx="7" ry="5" fill="#8E6436" opacity=".55"/>' for x, y in [(-90, -60), (70, -110), (95, 30), (-60, 90), (30, 120), (-105, 20)])
        return f'<path d="M0 {hy - h} C{w * 1.05} {hy - h * 1.02} {w * 1.08} {hy + h * .9} {w * .1} {hy + h} C{-w * 1.1} {hy + h * 1.05} {-w * 1.12} {hy - h * .95} 0 {hy - h}Z" fill="url(#g-potato)"/>' + spots + \
            f'<ellipse cx="{-w * .38}" cy="{hy - h * .5}" rx="{w * .3}" ry="{h * .25}" fill="url(#g-shine)"/>'
    return ""


def _human_head(c, hy, back):
    hair, hair2 = c["hair"], c["hair2"]
    if back:
        bun = f'<circle cx="10" cy="{hy - 175}" r="62" fill="{hair}"/><circle cx="-14" cy="{hy - 190}" r="34" fill="{hair2}" opacity=".6"/>'
        return bun + f'<path d="M-130 {hy - 20} C-150 {hy - 170} 150 {hy - 170} 130 {hy - 20} L140 {hy + 120} C100 {hy + 150} -100 {hy + 150} -140 {hy + 120}Z" fill="{hair}"/>'
    face = f'<ellipse cx="0" cy="{hy}" rx="112" ry="128" fill="url(#g-skin)"/>'
    ears = f'<ellipse cx="-110" cy="{hy + 10}" rx="16" ry="24" fill="#F0B892"/><ellipse cx="110" cy="{hy + 10}" rx="16" ry="24" fill="#F0B892"/>'
    fringe = f'<path d="M-118 {hy - 10} C-120 {hy - 150} 120 {hy - 150} 118 {hy - 10} C90 {hy - 95} 20 {hy - 118} -10 {hy - 112} C-60 {hy - 108} -100 {hy - 70} -118 {hy - 10}Z" fill="{hair}"/>'
    strands = f'<path d="M-112 {hy - 30} C-140 {hy + 40} -120 {hy + 110} -96 {hy + 140}" stroke="{hair2}" stroke-width="12" fill="none" stroke-linecap="round"/><path d="M112 {hy - 30} C140 {hy + 40} 120 {hy + 110} 96 {hy + 140}" stroke="{hair2}" stroke-width="12" fill="none" stroke-linecap="round"/>'
    blush = f'<ellipse cx="-62" cy="{hy + 48}" rx="22" ry="12" fill="#FF8F8F" opacity=".45"/><ellipse cx="62" cy="{hy + 48}" rx="22" ry="12" fill="#FF8F8F" opacity=".45"/>'
    nose = f'<path d="M-4 {hy + 30} Q4 {hy + 44} -8 {hy + 48}" stroke="#C98864" stroke-width="5" fill="none" stroke-linecap="round"/>'
    return ears + face + blush + nose + fringe + strands


def _eyes(cid, c, hy, expr, gaze, human):
    gx, gy = gaze
    ey = hy + (2 if human else -10)
    rx, ry, sep = (28, 34, 46) if human else (27, 31, 48)
    out = []
    for side, sx in (("l", -sep), ("r", sep)):
        if expr == "wink" and side == "r":
            out.append(f'<path d="M{sx - 24} {ey + 4} Q{sx} {ey - 14} {sx + 24} {ey + 4}" stroke="#2b1a10" stroke-width="7" fill="none" stroke-linecap="round"/>')
            continue
        iris = c.get("iris", "#3a2412")
        lid = ""
        if expr in ("disgust", "angry", "think", "smirk"):
            lid = f'<path d="M{sx - rx - 2} {ey - ry - 2} H{sx + rx + 2} V{ey - ry * .25} H{sx - rx - 2}Z" fill="{"url(#g-skin)" if human else "#00000000"}"/>' if human else \
                  f'<rect x="{sx - rx - 2}" y="{ey - ry - 2}" width="{2 * rx + 4}" height="{ry * .75}" fill="{ {"laugen": "#8A4218", "baguette": "#D89A4A", "potato": "#C29460"}[c["head"]] }"/>'
        big = 1.18 if expr in ("surprised",) else 1
        out.append(f'<g id="{cid}-eye{side}" data-cy="{ey}"><ellipse cx="{sx}" cy="{ey}" rx="{rx * big}" ry="{ry * big}" fill="#fff" stroke="rgba(0,0,0,.25)" stroke-width="2"/>'
                   f'<circle cx="{sx + gx * 9}" cy="{ey + gy * 9 + 3}" r="{16 if human else 14}" fill="{iris}"/>'
                   f'<circle cx="{sx + gx * 9}" cy="{ey + gy * 9 + 3}" r="{8 if human else 9}" fill="#140c06"/>'
                   f'<circle cx="{sx + gx * 9 + 5}" cy="{ey + gy * 9 - 3}" r="5" fill="#fff"/>{lid}</g>')
        if human:
            o = -1 if side == "l" else 1
            out.append(f'<path d="M{sx - o * rx * .9:.0f} {ey - ry * .62:.0f} Q{sx} {ey - ry * 1.3:.0f} {sx + o * rx * .98:.0f} {ey - ry * .5:.0f} l{o * 13} -9" stroke="#1d120b" stroke-width="5" fill="none" stroke-linecap="round"/>')
    bl, br, bdy = BROWS.get(expr, BROWS["neutral"])
    bc = "#3a2412" if human else "#2a1408"
    bw = 8 if human else 13
    by = ey - ry - (16 if human else 22) + bdy
    brows = (f'<path d="M{-sep - 26} {by + bl * .2} L{-sep + 24} {by - bl * .8}" stroke="{bc}" stroke-width="{bw}" stroke-linecap="round"/>'
             f'<path d="M{sep + 26} {by + br * .2} L{sep - 24} {by - br * .8}" stroke="{bc}" stroke-width="{bw}" stroke-linecap="round"/>')
    return f'<g id="{cid}-eyes">{"".join(out)}</g>' + brows


def fs(value, w):
    n = sum(ch.isdigit() for ch in str(value)) or 1
    return round(min(h_ := w * .17, (w - 56) / (n * .86)), 1)


def led(value):
    return "#3dff6e" if int(str(value).replace(".", "") or 0) >= 1000 else "#ff3b3b"


def display(cid, hy, human, value):
    dy = hy - (100 if human else 100)
    w, h = (150, 48) if human else (172, 56)
    return (f'<g id="{cid}-disp" filter="url(#shadow)"><rect x="{-w / 2}" y="{dy - h / 2}" width="{w}" height="{h}" rx="11" fill="#0d0d10" stroke="#3a3a42" stroke-width="3"/>'
            f'<rect x="{-w / 2 + 7}" y="{dy - h / 2 + 7}" width="{w - 14}" height="{h - 14}" rx="6" fill="#020203"/>'
            f'<g id="{cid}-scr" filter="url(#glow)"><text id="{cid}-dt" x="{w / 2 - 40}" y="{dy + h * .2}" text-anchor="end" font-family="DSEG7" font-size="{fs(value, w)}" fill="{led(value)}" data-w="{w}">{value}</text>'
            f'<text id="{cid}-de" x="{w / 2 - 20}" y="{dy + h * .22}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="{h * .5}" fill="{led(value)}">€</text></g></g>')


def character(name, cid, pose="down", expr="neutral", gaze=(0, 0), disp_value="0", seated=False, extra=""):
    c = C[name]
    human = c["kind"] == "human"
    hy = c["hy"]
    L = []
    if human:
        L.append(_human_head(c, hy, back=True))
    # legs
    if not seated:
        if c.get("dress"):
            L.append('<path d="M-46 -370 L-50 -30 M46 -370 L50 -30" stroke="url(#g-skin)" stroke-width="40" stroke-linecap="round"/>')
        else:
            L.append(f'<rect x="-92" y="-390" width="84" height="370" rx="30" fill="{c["pants"]}"/><rect x="8" y="-390" width="84" height="370" rx="30" fill="{c["pants"]}"/>')
        L.append(f'<ellipse cx="-56" cy="-14" rx="58" ry="24" fill="{c["shoe"]}"/><ellipse cx="56" cy="-14" rx="58" ry="24" fill="{c["shoe"]}"/>')
    # torso
    if human:
        if c.get("dress"):
            L.append('<path d="M-95 -640 Q0 -665 95 -640 L120 -330 Q0 -300 -120 -330Z" fill="url(#g-red)"/>'
                     '<path d="M-60 -640 Q0 -560 60 -640" fill="url(#g-skin)"/><path d="M-70 -640 L-55 -700 M70 -640 L55 -700" stroke="#C81E2A" stroke-width="6"/>')
        else:
            L.append('<path d="M-100 -645 Q0 -670 100 -645 L112 -380 Q0 -360 -112 -380Z" fill="#fff"/>'
                     '<path d="M-60 -652 Q0 -590 60 -652" fill="url(#g-skin)"/>'
                     '<path d="M-118 -640 L-40 -652 L-30 -380 L-122 -380Z" fill="url(#g-cardigan)" stroke="#d8cfc2" stroke-width="2"/>'
                     '<path d="M118 -640 L40 -652 L30 -380 L122 -380Z" fill="url(#g-cardigan)" stroke="#d8cfc2" stroke-width="2"/>'
                     '<path d="M-8 -600 L0 -585 L8 -600" stroke="#E7C36A" stroke-width="4" fill="none"/>')
    else:
        L.append(f'<path d="M-140 -655 Q0 -690 140 -655 L128 -370 Q0 -350 -128 -370Z" fill="{c["shirt"]}"/>')
        if c.get("vest"):
            L.append(f'<path d="M-70 -660 L0 -540 L70 -660 L100 -380 Q0 -360 -100 -380Z" fill="{c["vest"]}"/>')
        if c.get("bow"):
            L.append('<path d="M0 -650 L-38 -672 L-38 -628Z M0 -650 L38 -672 L38 -628Z" fill="#0a0a0a"/><circle cx="0" cy="-650" r="9" fill="#0a0a0a"/>')
        elif name == "Leo":
            L.append('<path d="M-36 -668 L0 -630 L36 -668" stroke="#3a3a44" stroke-width="7" fill="none"/>'
                     '<circle cx="0" cy="-590" r="5" fill="#555"/><circle cx="0" cy="-530" r="5" fill="#555"/><circle cx="0" cy="-470" r="5" fill="#555"/>'
                     '<rect x="-128" y="-400" width="256" height="22" fill="#0e0e10"/><rect x="-16" y="-402" width="32" height="26" rx="4" fill="#C8A64A"/>')
    # neck
    L.append(f'<rect x="-28" y="{hy + 100}" width="56" height="70" fill="{"url(#g-skin)" if human else c["hand"]}"/>' if human else "")
    # arms
    la, ra = ARMS[pose]
    sw = 40 if human else 50
    L.append(_arm(la, -118 if not human else -100, -630, c["sleeve"], c["hand"], sw, human))
    # head + face
    head = _human_head(c, hy, back=False) if human else _head(c, cid, hy)
    face = _eyes(cid, c, hy, expr, gaze, human)
    my = hy + (82 if human else 72)
    mouth = (f'<g transform="translate(0 {my})"><path id="{cid}-ms" d="{MOUTHS.get(expr, MOUTHS["neutral"])}" stroke="#4a1d10" stroke-width="{7 if human else 9}" fill="none" stroke-linecap="round"/>'
             f'<g id="{cid}-mt" transform="scale(1 0.05)"><ellipse cx="0" cy="10" rx="{26 if human else 34}" ry="{20 if human else 24}" fill="#4a1414"/>'
             f'<ellipse cx="0" cy="22" rx="{14 if human else 18}" ry="8" fill="#E06A6A"/></g></g>')
    disp = display(cid, hy, human, disp_value)
    L.append(f'<g id="{cid}-head">{head}{face}{mouth}{disp}</g>')
    L.append(_arm(ra, 118 if not human else 100, -630, c["sleeve"], c["hand"], sw, human))
    if pose == "notepad":
        L.append('<rect x="20" y="-560" width="110" height="140" rx="8" fill="#fff" stroke="#bbb" stroke-width="3" transform="rotate(-8 75 -490)"/>')
    if name == "Henri":
        L.append('<path d="M-150 -560 Q-120 -500 -150 -400 L-110 -400 Q-90 -500 -112 -560Z" fill="#fff" stroke="#ddd" stroke-width="3"/>')
    L.append(extra)
    return f'<g id="{cid}-bob">{"".join(L)}</g>'
