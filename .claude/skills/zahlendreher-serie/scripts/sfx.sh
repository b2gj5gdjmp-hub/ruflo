#!/usr/bin/env bash
# Synthesizes the series' sound effects into assets/sfx/ (run inside the episode folder). Free, no network.
set -e; mkdir -p assets/sfx
ffmpeg -v error -y -f lavfi -i "aevalsrc='0.5*sin(2*PI*(1800-700*t)*t)*exp(-60*mod(t\,0.055))':s=44100:d=1.1" -af "afade=t=out:st=0.9:d=0.2,volume=0.6" assets/sfx/roll.wav
ffmpeg -v error -y -f lavfi -i "anoisesrc=d=1.1:c=white:a=0.5:r=44100" -af "volume='if(lt(mod(t\,0.09)\,0.035)\,1\,0.05)':eval=frame,highpass=f=1500,afade=t=out:st=0.9:d=0.2,volume=0.5" assets/sfx/flicker.wav
ffmpeg -v error -y -f lavfi -i "aevalsrc='0.45*(sin(2*PI*55*t)+0.6*sin(2*PI*110*t)+0.3*sin(2*PI*82.4*t))*(lt(t\,0.22)+gte(t\,0.38)*lt(t\,0.6)+gte(t\,0.8)*exp(-1.6*(t-0.8)))':s=44100:d=2.2" -af "lowpass=f=900,afade=t=out:st=1.7:d=0.5" assets/sfx/sting.wav
