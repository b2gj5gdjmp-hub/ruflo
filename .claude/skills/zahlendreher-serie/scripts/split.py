import json,subprocess,re,difflib,sys,os
import sherpa_onnx, soundfile as sf, numpy as np
M="asr/sherpa-onnx-whisper-small/small-"
R=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=M+"encoder.int8.onnx",decoder=M+"decoder.int8.onnx",tokens=M+"tokens.txt",language="de",task="transcribe",num_threads=4)
def asr(a,sr):
    s=R.create_stream(); s.accept_waveform(sr,a); R.decode_stream(s); return s.result.text.strip()
norm=lambda t:re.sub(r"[^a-zäöüß ]","",t.lower().replace("…"," ")).split()
G=json.load(open("tools/groups.json")); res={}
for gid,g in G.items():
    f=f"voice/g{gid}.wav"; a,sr=sf.read(f,dtype="float32")
    out=subprocess.run(["ffmpeg","-i",f,"-af","silencedetect=noise=-40dB:d=0.22","-f","null","-"],capture_output=True,text=True).stderr
    s=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",out)]; e=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",out)]
    # speech chunks
    bounds=[]; t=0.0
    for a0,b0 in zip(s,e):
        if a0>t+0.05: bounds.append((t,a0))
        t=b0
    if len(a)/sr>t+0.05: bounds.append((t,len(a)/sr))
    chunks=[(st,en,asr(a[int(st*sr):int(en*sr)],sr)) for st,en in bounds]
    # DP alignment: assign consecutive chunks to lines maximizing similarity
    L=g["lines"]; n,m=len(L),len(chunks)
    from functools import lru_cache
    def sim(i,j,k): return difflib.SequenceMatcher(None,norm(L[i][2])," ".join(c[2] for c in chunks[j:k]).lower().split() and norm(" ".join(c[2] for c in chunks[j:k]))).ratio()
    @lru_cache(None)
    def best(i,j):
        if i==n: return (0,()) if j==m else (-99,())
        opts=[]
        for k in range(j+1,m-(n-i-1)+1):
            sc,rest=best(i+1,k); opts.append((sim(i,j,k)+sc,((j,k),)+rest))
        return max(opts) if opts else (-99,())
    sc,assign=best(0,0)
    for i,(j,k) in enumerate(assign):
        st,en=chunks[j][0],chunks[k-1][1]; txt=" ".join(c[2] for c in chunks[j:k])
        sid=g["ids"][i]; res[sid]={"start":round(st,3),"end":round(en,3),"group":gid,"asr":txt,"want":L[i][2]}
        print(gid,sid,f"{st:.2f}-{en:.2f}",round(sim(i,j,k),2),"|",txt,"||",L[i][2])
json.dump(res,open("voice/segments.json","w"),ensure_ascii=False,indent=1)
