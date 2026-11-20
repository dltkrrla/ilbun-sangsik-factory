"""31편 마스코트판(컷아웃 애니메이션) 합성 — Higgsfield 샌드박스에서 실행.
배경 그림 b0~b6 + 투명 캐릭터 포즈 p_*.png 를 프레임마다 움직여 bg.mp4 를 만들고, 오버레이(ov.webm)·소리(audio.m4a)를 얹는다.
usage: python3 comp_m31.py  (img/ 폴더와 ov.webm, audio.m4a 가 같은 폴더에 있어야 함)"""
import math, os, subprocess
from PIL import Image

W, H, FPS = 1080, 1920, 30
NB = [0.0, 2.58, 6.77, 11.27, 15.64, 19.94, 24.39, 27.67, 30.51]
DUR = NB[-1]
# 줄마다 (배경, 포즈, 배경 위로 올릴 픽셀, 줌 초점 x, y)
SHOTS = [("b0", "p_paint", 0, 0.55, 0.45), ("b1", "p_think", 0, 0.7, 0.4), ("b2", "p_aha", 0, 0.6, 0.45),
         ("b3", "p_wow", 0, 0.6, 0.5), ("b4", "p_explain", 0, 0.6, 0.4), ("b5", "p_explain", 330, 0.6, 0.5),
         ("b6", "p_aha", 0, 0.7, 0.4), ("b0", "p_paint", 0, 0.55, 0.45)]
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def load_bg(name, up):
    im = Image.open(f"img/{name}.png").convert("RGB").resize((W, int(W * 1344 / 752)), Image.LANCZOS)
    if up:
        c = Image.new("RGB", (W, im.height), im.getpixel((W // 2, im.height - 5)))
        bottom = im.crop((0, im.height - 10, W, im.height)).resize((W, up + 10))
        c.paste(im.crop((0, up, W, im.height)), (0, 0)); c.paste(bottom, (0, im.height - up - 10)); im = c
    return im.crop((0, 0, W, H)) if im.height >= H else im.resize((W, H))


BGS = {}
POSES = {}
for b, p, up, *_ in SHOTS:
    BGS.setdefault((b, up), load_bg(b, up))
    if p not in POSES:
        q = Image.open(f"img/{p}.png").convert("RGBA"); bb = q.getbbox(); q = q.crop(bb)
        s = 760 / q.height; POSES[p] = q.resize((int(q.width * s), 760), Image.LANCZOS)


def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)


def back(x):
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def frame(t):
    i = max(k for k in range(len(SHOTS)) if NB[k] <= t)
    b, p, up, fx, fy = SHOTS[i]; lt = t - NB[i]; d = NB[i + 1] - NB[i]
    bg = BGS[(b, up)]
    z = 1.0 + 0.06 * ease(lt / d) + 0.05 * (1 - ease(lt / 0.25))          # 컷마다 살짝 튀는 줌 + 천천히 다가감
    cw, ch = W / z, H / z; x0 = (W - cw) * fx; y0 = (H - ch) * fy
    im = bg.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR).convert("RGBA")
    pose = POSES[p]
    k = back(lt / 0.32)                                                     # 등장: 아래에서 튀어 오름
    sy = 1 + 0.06 * math.sin(t * 5.2)                                       # 숨쉬기
    sc = (0.6 + 0.4 * k)
    if p == "p_wow" and lt < 0.5:
        sc *= 1 + 0.12 * math.sin(lt / 0.5 * math.pi)
    w2, h2 = int(pose.width * sc), int(pose.height * sc * sy)
    q = pose.resize((max(1, w2), max(1, h2)), Image.BILINEAR)
    ang = 2.2 * math.sin(t * 2.6) + (6 * math.sin(lt * 9) * max(0, 1 - lt / 1.2) if p == "p_paint" else 0)
    q = q.rotate(ang, resample=Image.BICUBIC, expand=True)
    hop = -60 * math.sin(min(1, lt / 0.35) * math.pi) if p in ("p_aha", "p_wow") else 0
    cx, foot = 250, 1335 + (1 - k) * 260 + hop
    im.alpha_composite(q, (int(cx - q.width / 2), int(foot - q.height)))
    return im.convert("RGB")


tmp = "bg_m31.part.mp4"
pr = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
for n in range(int(round(DUR * FPS))):
    pr.stdin.write(frame(n / FPS).tobytes())
pr.stdin.close(); assert pr.wait() == 0
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-c:v", "libvpx-vp9", "-i", "ov.webm", "-i", "audio.m4a",
                "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]", "-map", "[v]", "-map", "2:a",
                "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-t", str(DUR), "-movflags", "+faststart", "ep31m.part.mp4"], check=True)
os.replace("ep31m.part.mp4", "ep31m.mp4"); print("ok ep31m.mp4", DUR)
