# Builds teil-01/index.html from tools/shots.json, voice/segments.json and tools/displays.json
import json, os
S = json.load(open("tools/shots.json")); V = json.load(open("voice/segments.json"))
D = json.load(open("tools/displays.json")) if os.path.exists("tools/displays.json") else {}
GAP, SCENE_GAP, LEAD = 0.22, 0.35, 0.12
t = 0.0; shots = []; audios = []; prev_scene = None
for s in S:
    if prev_scene and s["scene"] != prev_scene: t += SCENE_GAP - GAP
    start = t; cur = t + LEAD
    for lid in s["lines"]:
        audios.append((lid, round(cur, 3), V[lid]["dur"])); cur += V[lid]["dur"] + GAP
    end = max(cur, start + 0.8) + s.get("hold", 0)
    if not s["lines"]: end = start + s.get("hold", 1.5)
    shots.append({**s, "start": round(start, 3), "dur": round(end - start, 3)}); t = end; prev_scene = s["scene"]
TOTAL = round(t + 0.6, 3)
def disp_html(sid, i, d):
    v = d["values"][0][1]
    return (f'<div class="disp" id="d{sid}_{i}" style="left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;transform:translate(-50%,-50%) rotate({d.get("rot",0)}deg)">'
            f'<div class="scr"><span class="num" id="n{sid}_{i}">{fmt(v)}</span><span class="eur">€</span></div></div>')
def fmt(v): return f"{int(v):,}".replace(",", ".")
shot_html = []; js = []
for k, s in enumerate(shots):
    sid = s["id"]; disps = D.get(sid, [])
    inner = "".join(disp_html(sid, i, d) for i, d in enumerate(disps))
    shot_html.append(f'<div id="s{sid}" class="clip shot" data-start="{s["start"]}" data-duration="{s["dur"]}" data-track-index="1" style="z-index:{k+1}">'
                     f'<div class="cam" id="c{sid}"><img src="assets/shots/s{sid}.png" alt="">{inner}</div></div>')
    # camera move: alternate push-in / drift
    mv = ["{scale:1.0}|{scale:1.07}", "{scale:1.08,x:-18}|{scale:1.08,x:18}", "{scale:1.06}|{scale:1.0}", "{scale:1.08,x:16}|{scale:1.08,x:-16}"][k % 4].split("|")
    js.append(f'tl.fromTo("#c{sid}",{mv[0]},{{...{mv[1]},duration:{s["dur"]},ease:"none"}},{s["start"]});')
    for i, d in enumerate(disps):
        # values: [[t_rel, value], ...] ; color by amount
        prev = None
        for tr, val in d["values"]:
            col = "#3dff6e" if val >= 1000 else "#ff3b3b"
            at = round(s["start"] + tr, 3)
            if prev is None:
                js.append(f'tl.set("#n{sid}_{i}",{{textContent:"{fmt(val)}"}},{s["start"]});tl.set("#d{sid}_{i}",{{"--led":"{col}"}},{s["start"]});')
            else:
                dur = d.get("roll", 1.0)
                js.append(f'(()=>{{const o={{v:{prev}}};tl.to(o,{{v:{val},duration:{dur},ease:"power2.inOut",onUpdate:()=>{{document.getElementById("n{sid}_{i}").textContent=fmtE(o.v)}}}},{at});}})();')
                js.append(f'tl.set("#d{sid}_{i}",{{"--led":"{col}"}},{round(at+dur*0.5,3)});')
                js.append(f'tl.fromTo("#d{sid}_{i} .scr",{{opacity:1}},{{opacity:0.35,duration:0.05,yoyo:true,repeat:5}},{at});')
            prev = val
audio_html = [f'<audio id="a{lid}" class="clip" data-start="{st}" data-duration="{du}" data-track-index="2" src="assets/voice/l{lid}.wav"></audio>' for lid, st, du in audios]
html = f'''<!doctype html>
<html lang="de" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
@font-face {{ font-family: "DSEG7"; src: url("assets/fonts/DSEG7Classic-Bold.woff2") format("woff2"); }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1920px; overflow:hidden; background:#000; }}
#root {{ width:100%; height:100%; position:relative; overflow:hidden; background:#000; }}
.shot {{ position:absolute; inset:0; overflow:hidden; }}
.cam {{ position:absolute; inset:0; transform-origin:50% 42%; }}
.cam img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.disp {{ position:absolute; aspect-ratio: 3.1 / 1; --led:#ff3b3b; background:linear-gradient(#1c1c1f,#050506);
  border-radius:12%/30%; padding:5% 6%; box-shadow:0 4px 10px rgba(0,0,0,.55), inset 0 1px 1px rgba(255,255,255,.18); container-type:inline-size; }}
.scr {{ width:100%; height:100%; background:#020203; border-radius:6%/20%; display:flex; align-items:center; justify-content:center; gap:2cqw;
  box-shadow: inset 0 0 8px rgba(0,0,0,.9); }}
.num {{ font-family:"DSEG7", monospace; font-size:16cqw; color:var(--led); text-shadow:0 0 2cqw var(--led), 0 0 5cqw var(--led); letter-spacing:.5cqw; white-space:nowrap; }}
.eur {{ font-family:"Inter", sans-serif; font-weight:800; font-size:15cqw; color:var(--led); text-shadow:0 0 2cqw var(--led); }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
{chr(10).join(shot_html)}
{chr(10).join(audio_html)}
</div>
<script>
const fmtE = v => Math.round(v).toLocaleString("de-DE");
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
window.__timelines["main"] = tl;
tl.seek(0);
</script>
</body>
</html>
'''
open("teil-01/index.html", "w").write(html)
json.dump(shots, open("tools/timing.json", "w"), indent=1)
print("total", TOTAL, "shots", len(shots))
for s in shots: print(s["id"], s["start"], s["dur"])
