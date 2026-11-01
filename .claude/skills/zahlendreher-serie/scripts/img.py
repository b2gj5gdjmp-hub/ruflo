# usage: img.py OUT.png "prompt" [ref1.png ref2.png ...]  (model via ZD_IMG_MODEL)
import sys, os, json, base64, urllib.request
out, prompt, refs = sys.argv[1], sys.argv[2], sys.argv[3:]
model = os.environ.get("ZD_IMG_MODEL", "gemini-3.1-flash-image")
key = open(os.path.expanduser("~/.zd/key")).read().strip()
parts = [{"inline_data": {"mime_type": "image/png", "data": base64.b64encode(open(r, "rb").read()).decode()}} for r in refs]
parts.append({"text": prompt})
body = {"contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": os.environ.get("ZD_AR", "9:16")}}}
req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "x-goog-api-key": key})
try:
    d = json.load(urllib.request.urlopen(req, timeout=300))
except urllib.error.HTTPError as e:
    sys.exit(f"HTTP {e.code}: {e.read().decode()[:400]}")
for c in d.get("candidates", []):
    for p in c.get("content", {}).get("parts", []):
        b = p.get("inline_data") or p.get("inlineData")
        if b:
            open(out, "wb").write(base64.b64decode(b["data"])); print("ok", out); sys.exit(0)
sys.exit("no image: " + json.dumps(d)[:400])
