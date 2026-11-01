# Backgrounds (1080x1920) and foreground props for @zahlendreher.tv cartoon episodes.
import random


def _bokeh(seed, n, y0, y1, colors, rmin=14, rmax=46, op=(.25, .6)):
    r = random.Random(seed)
    return "".join(f'<circle cx="{r.uniform(-40, 1120):.0f}" cy="{r.uniform(y0, y1):.0f}" r="{r.uniform(rmin, rmax):.0f}" fill="{r.choice(colors)}" opacity="{r.uniform(*op):.2f}"/>' for _ in range(n))


def _skyline(seed, base, h0, h1, color, lights=None):
    r = random.Random(seed); x = -20; out = []
    while x < 1100:
        w = r.uniform(50, 120); h = r.uniform(h0, h1)
        out.append(f'<rect x="{x:.0f}" y="{base - h:.0f}" width="{w:.0f}" height="{h + 400:.0f}" fill="{color}"/>')
        if lights:
            for _ in range(int(h / 30)):
                out.append(f'<rect x="{x + r.uniform(6, w - 12):.0f}" y="{base - r.uniform(10, h - 10):.0f}" width="7" height="9" fill="{lights}" opacity="{r.uniform(.4, .95):.2f}"/>')
        x += w + r.uniform(-8, 12)
    return "".join(out)


def dressing():
    shelves = []
    r = random.Random(3)
    for col, x in enumerate([40, 300, 780]):
        shelves.append(f'<rect x="{x}" y="520" width="{260 if col != 2 else 300}" height="1000" fill="#5A3518"/>')
        shelves.append(f'<rect x="{x + 14}" y="540" width="{232 if col != 2 else 272}" height="960" fill="#3B220F"/>')
        for i in range(7):
            c = r.choice(["#1d2433", "#2b2b30", "#4b3a2a", "#e9e3d6", "#20283a", "#5c1f24"])
            shelves.append(f'<rect x="{x + 22 + i * 32}" y="580" width="28" height="{r.uniform(300, 380):.0f}" rx="6" fill="{c}"/>')
        shelves.append(f'<rect x="{x + 14}" y="1080" width="{232 if col != 2 else 272}" height="14" fill="#7A4A22"/>')
        for i in range(4):
            shelves.append(f'<ellipse cx="{x + 50 + i * 55}" cy="1210" rx="24" ry="12" fill="{r.choice(["#2a1a10", "#111", "#5b3214"])}"/>')
    window = ('<rect x="560" y="300" width="220" height="760" fill="url(#bg-dusk)"/>'
              + f'<g clip-path="url(#win-clip)">{_skyline(5, 1060, 150, 520, "#2b2350", "#FFD27A")}</g>'
              + '<rect x="556" y="296" width="228" height="768" fill="none" stroke="#6E4524" stroke-width="16"/>')
    lamps = "".join(f'<circle cx="{x}" cy="230" r="120" fill="#FFC56B" opacity=".35" filter="url(#soft)"/><circle cx="{x}" cy="230" r="16" fill="#FFE7B0"/>' for x in (180, 540, 900))
    return (f'<defs><linearGradient id="bg-dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3B2F6B"/><stop offset=".6" stop-color="#C46A6A"/><stop offset="1" stop-color="#F2A65A"/></linearGradient>'
            f'<clipPath id="win-clip"><rect x="560" y="300" width="220" height="760"/></clipPath></defs>'
            f'<rect width="1080" height="1920" fill="#7A4B28"/><rect width="1080" height="1920" fill="url(#warm-wall)"/>'
            f'{window}{"".join(shelves)}{lamps}<rect y="1500" width="1080" height="420" fill="#6B3E1E"/>'
            f'<ellipse cx="540" cy="1640" rx="420" ry="90" fill="#3A2340" opacity=".85"/>')


def park():
    trees = "".join(f'<rect x="{x - 14}" y="{y}" width="28" height="420" fill="#4A3020"/>'
                    f'<circle cx="{x}" cy="{y}" r="{s}" fill="#4F8A3A"/><circle cx="{x - s * .5}" cy="{y + 40}" r="{s * .7}" fill="#5E9C44"/><circle cx="{x + s * .55}" cy="{y + 30}" r="{s * .75}" fill="#6FAE4F"/>'
                    for x, y, s in [(60, 820, 190), (1010, 780, 210), (330, 900, 120), (760, 880, 140)])
    flowers = _bokeh(11, 70, 1330, 1520, ["#FF7FA8", "#FFD15C", "#FFFFFF", "#C77DFF"], 6, 12, (.8, 1))
    lamps = "".join(f'<rect x="{x - 6}" y="980" width="12" height="440" fill="#2A2A30"/><circle cx="{x}" cy="975" r="26" fill="#FFE2A0"/><circle cx="{x}" cy="975" r="80" fill="#FFD27A" opacity=".35" filter="url(#soft)"/>' for x in (210, 880))
    return (f'<defs><linearGradient id="bg-gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7EB6E8"/><stop offset=".55" stop-color="#F9D7A0"/><stop offset="1" stop-color="#F7B46E"/></linearGradient></defs>'
            f'<rect width="1080" height="1920" fill="url(#bg-gold)"/><circle cx="820" cy="760" r="120" fill="#FFF1C4" opacity=".9" filter="url(#soft)"/>'
            f'{_skyline(9, 1100, 160, 560, "#9AA9C8")}{_skyline(19, 1150, 80, 300, "#7F8FB2")}'
            f'<rect y="1100" width="1080" height="820" fill="#7DB257"/>{trees}{lamps}'
            f'<path d="M300 1920 L470 1250 L610 1250 L780 1920Z" fill="#E7D3AE"/>{flowers}'
            f'<rect x="700" y="1290" width="200" height="16" rx="6" fill="#7A4A22"/><rect x="700" y="1250" width="200" height="14" rx="6" fill="#7A4A22"/>')


def restaurant():
    lights = "".join(f'<circle cx="{x}" cy="{220 + 40 * ((x // 90) % 2)}" r="10" fill="#FFE2A0"/>' for x in range(30, 1080, 90))
    return (f'<defs><linearGradient id="bg-night" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E1638"/><stop offset=".7" stop-color="#2B2A5E"/><stop offset="1" stop-color="#5A3A5E"/></linearGradient></defs>'
            f'<rect width="1080" height="1920" fill="url(#bg-night)"/>'
            f'{_skyline(31, 1050, 200, 700, "#141a3a", "#FFD27A")}{_skyline(41, 1080, 100, 320, "#1b2048", "#FFC56B")}'
            f'<rect y="1050" width="1080" height="70" fill="#1A2550"/>'
            f'<path d="M-20 200 Q540 330 1100 200" stroke="#333" stroke-width="3" fill="none"/>{lights}'
            f'{_bokeh(33, 40, 150, 1100, ["#FFC56B", "#FFE2A0", "#FF9E5E"], 18, 60)}'
            f'<rect y="1120" width="1080" height="800" fill="#3B2216"/>'
            f'{_bokeh(35, 18, 1150, 1500, ["#FFC56B"], 30, 80, (.15, .35))}')


def bar():
    r = random.Random(52)
    bottles = "".join(f'<rect x="{x}" y="{y - h}" width="34" height="{h}" rx="10" fill="{r.choice(["#2E6B3A", "#7A3B1E", "#C9A043", "#2F4F7A", "#8E2B3A"])}" opacity=".9"/>'
                      f'<rect x="{x + 11}" y="{y - h - 30}" width="12" height="34" fill="#222"/>'
                      for y in (620, 900, 1180) for x in range(40, 1060, 62) for h in [r.uniform(110, 170)])
    return (f'<rect width="1080" height="1920" fill="#2A170D"/>'
            f'<rect x="0" y="380" width="1080" height="900" fill="#3D2414"/>'
            + "".join(f'<rect x="0" y="{y}" width="1080" height="18" fill="#6E4524"/>' for y in (620, 900, 1180))
            + bottles + _bokeh(53, 30, 100, 1300, ["#FFC56B", "#FFE2A0"], 20, 70, (.2, .45))
            + '<rect y="1280" width="1080" height="640" fill="#4A2A15"/>')


SCENES = {"A": dressing, "B": park, "C": restaurant, "D": bar, "E": restaurant}

WALL = '<radialGradient id="warm-wall" cx="50%" cy="20%" r="90%"><stop offset="0" stop-color="#C98A4E" stop-opacity=".7"/><stop offset="1" stop-color="#3A2010" stop-opacity=".6"/></radialGradient>'


def table(y, items=("water", "water", "candle")):
    """Round restaurant table seen from the front; top edge at y."""
    out = [f'<ellipse cx="540" cy="{y}" rx="560" ry="70" fill="#7A4A26"/><rect x="-20" y="{y}" width="1120" height="900" fill="#5C3519"/>'
           f'<ellipse cx="540" cy="{y - 6}" rx="545" ry="60" fill="#8E5A30"/>']
    xs = {"water": [260, 820], "candle": [540], "lobster": [540], "champagne": [330, 750]}
    used = {}
    for it in items:
        i = used.get(it, 0); used[it] = i + 1; x = xs[it][min(i, len(xs[it]) - 1)]
        if it == "water":
            out.append(f'<path d="M{x - 34} {y - 150} L{x + 34} {y - 150} L{x + 28} {y - 8} L{x - 28} {y - 8}Z" fill="#CFE8F7" opacity=".55" stroke="#fff" stroke-width="3"/>'
                       f'<path d="M{x - 30} {y - 110} L{x + 30} {y - 110} L{x + 27} {y - 10} L{x - 27} {y - 10}Z" fill="#9FD0F0" opacity=".55"/><circle cx="{x + 8}" cy="{y - 120}" r="16" fill="#F2E34C" stroke="#D9C230" stroke-width="3"/>')
        if it == "candle":
            out.append(f'<rect x="{x - 26}" y="{y - 90}" width="52" height="84" rx="8" fill="#FFF4DC"/><circle cx="{x}" cy="{y - 110}" r="70" fill="#FFC56B" opacity=".45" filter="url(#soft)"/>'
                       f'<path d="M{x} {y - 128} Q{x + 12} {y - 104} {x} {y - 92} Q{x - 12} {y - 104} {x} {y - 128}Z" fill="#FFB43A"/>')
        if it == "lobster":
            out.append(f'<ellipse cx="{x}" cy="{y - 12}" rx="210" ry="40" fill="#fff" stroke="#ddd" stroke-width="4"/>'
                       f'<ellipse cx="{x}" cy="{y - 48}" rx="120" ry="44" fill="#E2432E"/><path d="M{x - 110} {y - 60} q-70 -60 -40 -110 q30 30 10 60 M{x + 110} {y - 60} q70 -60 40 -110 q-30 30 -10 60" stroke="#E2432E" stroke-width="26" fill="none" stroke-linecap="round"/>'
                       f'<circle cx="{x - 30}" cy="{y - 74}" r="8" fill="#111"/><circle cx="{x + 30}" cy="{y - 74}" r="8" fill="#111"/>')
        if it == "champagne":
            out.append(f'<path d="M{x - 30} {y - 220} Q{x} {y - 110} {x + 30} {y - 220}Z" fill="#F7E08A" opacity=".85" stroke="#fff" stroke-width="3"/><rect x="{x - 3}" y="{y - 160}" width="6" height="150" fill="#eee"/><ellipse cx="{x}" cy="{y - 10}" rx="34" ry="8" fill="#eee"/>')
    return "".join(out)


def counter(y):
    return f'<rect x="-20" y="{y}" width="1120" height="900" fill="#5A3218"/><rect x="-20" y="{y - 30}" width="1120" height="44" rx="10" fill="#8E5A30"/>'
