# usage: tts_multi.py MODEL GROUP_ID  -> voice/gGROUP.wav
import json, os, sys, base64, urllib.request, wave
model, gid = sys.argv[1], sys.argv[2]
key = open(os.path.expanduser("~/.zd/key")).read().strip()
VOICE = {"Leo":"Puck","Henri":"Charon","Chantal":"Zephyr","Mia":"Leda","Karl":"Algenib"}
G = json.load(open("tools/groups.json"))[gid]
speakers = sorted({s for s,_,_ in G["lines"]})
script = G["direction"] + "\n\n" + "\n".join(f"{s}: {('('+d+') ') if d else ''}{t}" for s,d,t in G["lines"])
body = {"contents":[{"parts":[{"text":script}]}],
  "generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"multiSpeakerVoiceConfig":{"speakerVoiceConfigs":[
     {"speaker":s,"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":VOICE[s]}}} for s in speakers]}}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
  data=json.dumps(body).encode(), headers={"Content-Type":"application/json","x-goog-api-key":key})
try: d = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e: sys.exit(f"HTTP {e.code} {e.read().decode()[:300]}")
p = d["candidates"][0]["content"]["parts"][0]["inlineData"]; raw = base64.b64decode(p["data"]); mt = p["mimeType"]
os.makedirs("voice", exist_ok=True); out = f"voice/g{gid}.wav"
if "wav" in mt: open(out,"wb").write(raw)
else:
    rate = int(mt.split("rate=")[1].split(";")[0]) if "rate=" in mt else 24000
    w = wave.open(out,"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(raw); w.close()
print("ok", out, mt)
