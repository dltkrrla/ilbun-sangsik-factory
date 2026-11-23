"""47편 합성 (Higgsfield 샌드박스에서 실행): 아저씨 연기 3개 + 설계도 5개 → 이어 붙이기 → 오버레이 → 소리.
usage: python3 comp47.py <dir> out.mp4   (dir 안에: cA cB cC .mp4, sc_*.mp4, ov47.webm, a47.m4a, segs.json)"""
import json, subprocess, sys, os
d = sys.argv[1]; out = sys.argv[2]
segs = json.load(open(f"{d}/segs.json"))      # [{"kind":"clip"|"scene","src":..,"dur":..,"zoom":bool}]
def run(a): subprocess.run(a, check=True)
parts = []
for i, sg in enumerate(segs):
    o = f"{d}/seg{i}.mp4"; tmp = f"{d}/seg{i}.part.mp4"; tgt = sg["dur"]
    if sg["kind"] == "clip":
        info = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{d}/{sg['src']}"]).split()[0])
        sp = min(max(info / tgt, 0.84), 1.25)
        vf = "scale=1080:1920:flags=lanczos"
        if sg.get("zoom"):
            vf = ("scale=w='trunc(1080*(1+0.32*min(1,n/54))/2)*2':h=-2:eval=frame:flags=bicubic,"
                  "crop=1080:1920:x='max(0,min(in_w-1080,in_w*0.66-540))':y='max(0,min(in_h-1920,in_h*0.32-960))'")
            vf = "scale=1080:1920:flags=lanczos," + vf
        vf += f",setpts=PTS/{sp},fps=30,tpad=stop_mode=clone:stop_duration=3,trim=duration={tgt:.3f},setpts=PTS-STARTPTS,format=yuv420p"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{d}/{sg['src']}", "-vf", vf, "-an", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp])
    else:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{d}/{sg['src']}", "-vf", f"fps=30,trim=duration={tgt:.3f},setpts=PTS-STARTPTS,format=yuv420p", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp])
    os.replace(tmp, o); parts.append(o)
open(f"{d}/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{d}/list.txt", "-c", "copy", f"{d}/cat.mp4"])
tmp = out + ".part.mp4"
run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{d}/cat.mp4", "-c:v", "libvpx-vp9", "-i", f"{d}/ov47.webm", "-i", f"{d}/a47.m4a",
     "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
     "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp])
os.replace(tmp, out); print("ok", out)
