"""50편 노란 점자블록 두 가지 모양 — 설계도 3장면.
blocks: 선형블록(줄=진행) / 점형블록(점=멈춤) 입체 확대 · map: 위에서 본 거리, 선형 따라가다 횡단보도·계단 앞 점형 · fine: 블록 위 물건 = 과태료 50만 원
사실: 점형블록 = 승강기·계단 등 시설 표시, 장애물 주위 위험 표시, 선형 시작·교차·굴절 지점(서울 내손안에서울 2023) · 진행=선형, 멈춤=점형(뉴스토마토) ·
점자블록 위 차량·물건 방치 금지, 과태료 50만 원(한국경제 2026-08).
usage: python3 bp50.py <scene> out.mp4 dur | out.jpg t1 t2 ...  (장면 타이밍은 PH 로 조절)"""
import math, os, subprocess, sys, json
from PIL import Image
from bp30v2 import W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back, LINE, CYAN, YEL, HOT, COLD
from bp40 import lerp, mix, GREEN, DIM, BG_N

TY = (255, 204, 40); TY_D = (176, 128, 10); TY_L = (255, 236, 140); RED = (255, 90, 80); MINT = (110, 230, 170)
PH = {"tile2": 3.2, "map_cross": 1.4, "map_stair": 3.0}
if os.path.exists("/home/claude/work/ph50.json"):
    PH.update(json.load(open("/home/claude/work/ph50.json")))


def tile(c, x, y, s, a, kind, lift=1.0):
    """노란 점자블록 한 장(입체). kind = 'line' | 'dot'."""
    h = s / 2
    c.rrect((x - h + 10, y - h + 14, x + h + 10, y + h + 14), s * 0.08, fill=(4, 14, 32), a=a * 0.6)
    c.rrect((x - h, y - h, x + h, y + h), s * 0.08, fill=TY_D, a=a)
    c.rrect((x - h, y - h, x + h - 4, y + h - 6), s * 0.08, fill=TY, a=a)
    if kind == "lineh":
        for i in range(4):
            by = y - h + s * (0.14 + 0.24 * i)
            bw = s * 0.11
            c.rrect((x - h + s * 0.08 + 4, by + 6 * lift, x + h - s * 0.08 + 4, by + bw + 6 * lift), bw / 2, fill=TY_D, a=a)
            c.rrect((x - h + s * 0.08, by, x + h - s * 0.08, by + bw), bw / 2, fill=TY, a=a)
        return
    if kind == "line":
        for i in range(4):
            bx = x - h + s * (0.14 + 0.24 * i)
            bw = s * 0.11
            c.rrect((bx + 4, y - h + s * 0.08 + 6 * lift, bx + bw + 4, y + h - s * 0.08 + 6 * lift), bw / 2, fill=TY_D, a=a)
            c.rrect((bx, y - h + s * 0.08, bx + bw, y + h - s * 0.08), bw / 2, fill=TY, a=a)
            c.rrect((bx + bw * 0.18, y - h + s * 0.1, bx + bw * 0.45, y + h - s * 0.12), bw / 4, fill=TY_L, a=a * 0.9)
    else:
        n = 6
        for i in range(n):
            for j in range(n):
                cx = x - h + s * (0.1 + 0.8 * (i + 0.5) / n); cy = y - h + s * (0.1 + 0.8 * (j + 0.5) / n)
                r = s * 0.055
                c.circle(cx + 3, cy + 5 * lift, r, fill=TY_D, a=a)
                c.circle(cx, cy, r, fill=TY, a=a)
                c.circle(cx - r * 0.3, cy - r * 0.3, r * 0.38, fill=TY_L, a=a * 0.9)


# ---------------------------------------------------------------- 1. 두 가지 모양
def cane(c, cx, cy, t, a=1.0):
    for m in range(3):
        r = 18 + 26 * (((t * 2) + m / 3) % 1)
        c.circle(cx, cy, r, outline=(255, 255, 255), w=3, a=a * 0.5 * (1 - (r - 18) / 26))
    c.line([(cx, cy), (cx + 90, cy + 220)], (255, 255, 255), 8, a * 0.95)
    c.line([(cx + 66, cy + 160), (cx + 90, cy + 220)], (220, 60, 60), 10, a * 0.95)
    c.circle(cx, cy, 13, fill=(255, 255, 255), a=a)


def blocks(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 50-A  |  점자블록 두 가지")
    a0 = ease(t / 0.25)
    T1, T2 = PH.get("tile1", 6.2), PH.get("tile2", 9.6)
    k0 = back((t - 0.1) / 0.45)
    km = ease((t - T1) / 0.5)
    x, y = lerp(540, 330, km), lerp(720, 450, km)
    s1 = lerp(560, 330, km) * max(min(k0, 1.2), 0.05)
    tile(c, x, y, s1, a0, "line")
    if t < T1 + 0.2:
        fa = 1 - ease((t - T1) / 0.2)
        c.text(540, 340, "눈이 안 보이는 분들이", 46, LINE, a0 * fa)
        c.text(540, 410, "\u2018읽는\u2019 길", 64, TY, a0 * fa * ease((t - 0.5) / 0.3), stroke=3)
        # 지팡이 끝이 줄을 따라 톡톡
        ph = (t * 0.6) % 1
        cane(c, 540 - 70 + 140 * (int(t * 1.7) % 2), lerp(980, 470, ph), t, a0 * fa * ease((t - 0.8) / 0.3))
        cs, ce = PH.get("cta", 3.0), PH.get("cta_end", 6.2)
        if cs < t < ce + 0.2:
            ka = ease((t - cs) / 0.3) * (1 - ease((t - ce) / 0.2))
            pul = 1 + 0.05 * math.sin(t * 8)
            c.rrect((540 - 330 * pul, 1110 - 52 * pul, 540 + 330 * pul, 1110 + 52 * pul), 52, fill=MINT, a=ka)
            c.rrect((540 - 300, 1110 - 30, 540 - 262, 1110 + 30), 8, fill=(20, 60, 40), a=ka)
            c.text(540 + 20, 1110, "친구\u00b7가족에게 보내기", 44, (10, 40, 24), ka)
    if t > T1 + 0.4:
        ka = ease((t - T1 - 0.4) / 0.3)
        c.text(640, 400, "선형블록", 44, TY, ka, anchor="lm", stroke=2)
        c.text(640, 470, "줄 = 쭉 가세요", 40, LINE, ka, anchor="lm")
        for m in range(3):
            k = ((t * 0.9 + m / 3) % 1)
            yy = lerp(600, 300, k)
            c.poly([(330 - 26, yy + 20), (330 + 26, yy + 20), (330, yy - 20)], MINT, (1 - abs(k - 0.5) * 2) * ka)
    k2 = back((t - T2) / 0.45)
    if t > T2:
        tile(c, 330, 900, 330 * max(k2, 0.05), 1, "dot")
        kb = ease((t - T2 - 0.5) / 0.3)
        c.text(640, 850, "점형블록", 44, TY, kb, anchor="lm", stroke=2)
        c.text(640, 920, "점 = 멈추세요", 40, LINE, kb, anchor="lm")
        if t > T2 + 0.6:
            pul = 0.5 + 0.5 * math.sin((t - T2) * 7)
            c.rrect((330 - 185, 900 - 185, 330 + 185, 900 + 185), 30, outline=RED, w=6, a=0.4 + 0.5 * pul)
            hx, hy = 1000, 885
            c.circle(hx, hy, 46, fill=RED, a=kb)
            c.rrect((hx - 22, hy - 18, hx + 22, hy + 26), 10, fill=(255, 255, 255), a=kb)
            for f in range(4):
                c.rrect((hx - 22 + f * 12, hy - 34, hx - 14 + f * 12, hy - 10), 4, fill=(255, 255, 255), a=kb)
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


# ---------------------------------------------------------------- 2. 위에서 본 거리
def map_(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 50-B  |  위에서 본 보도")
    a0 = ease(t / 0.25)
    # 보도 (회색 띠) + 차도 + 횡단보도 + 계단
    c.rrect((60, 300, 1020, 1180), 30, fill=(54, 64, 80), a=a0)
    c.rrect((60, 300, 1020, 420), 30, fill=(30, 34, 44), a=a0)                    # 차도(위)
    for i in range(7):
        c.rrect((380 + i * 50, 304, 404 + i * 50, 416), 4, fill=(230, 234, 240), a=a0)  # 횡단보도
    c.text(230, 360, "횡단보도", 34, LINE, a0)
    for i in range(5):
        c.rrect((820, 900 + i * 44, 1010, 930 + i * 44), 4, fill=(110, 120, 140), a=a0)  # 계단(오른쪽 아래)
    c.text(915, 880, "계단", 32, LINE, a0)
    # 블록 경로: 아래에서 위로 선형, 횡단보도 앞 점형 / 중간에서 오른쪽으로 선형, 계단 앞 점형
    ts = 56
    path_up = [(520, 1150 - i * ts) for i in range(13)]            # 1150 → 478
    path_r = [(520 + (i + 1) * ts, 940) for i in range(4)]         # → 744
    grow = ease((t - 0.1) / 0.9)
    nup = int(len(path_up) * grow)
    for i, (x, y) in enumerate(path_up[:nup]):
        tile(c, x, y, ts - 6, a0, "line", lift=0.4)
    for i, (x, y) in enumerate(path_r[:int(len(path_r) * grow)]):
        tile(c, x, y, ts - 6, a0, "lineh", lift=0.4)
    tile(c, 520, 1150 - 12 * ts, ts - 6, 0, "line")
    # 점형: 횡단보도 앞 한 줄, 계단 앞 한 줄
    kc = back((t - PH["map_cross"]) / 0.4)
    if kc > 0:
        for j in range(-3, 4):
            tile(c, 520 + j * ts, 450, (ts - 6) * min(1, kc), 1, "dot", lift=0.4)
        c.rrect((520 - 3.5 * ts - 10, 450 - ts / 2 - 10, 520 + 3.5 * ts + 10, 450 + ts / 2 + 10), 14, outline=RED, w=5, a=0.6 + 0.4 * math.sin(t * 7))
    ks = back((t - PH["map_stair"]) / 0.4)
    if ks > 0:
        for j in range(-2, 3):
            tile(c, 790, 940 + j * ts, (ts - 6) * min(1, ks), 1, "dot", lift=0.4)
        c.rrect((790 - ts / 2 - 10, 940 - 2.5 * ts - 10, 790 + ts / 2 + 10, 940 + 2.5 * ts + 10), 14, outline=RED, w=5, a=0.6 + 0.4 * math.sin(t * 7))
    # 지팡이 끝이 경로를 따라감: 위로 → 횡단보도 앞 멈춤 → 아래로 갈림길 → 오른쪽 계단 앞 멈춤
    if t > 0.5:
        mc, ms = PH["map_cross"], PH["map_stair"]
        if t < mc:
            k = eout((t - 0.5) / max(0.3, mc - 0.5)); cx, cy = 560, lerp(1150, 520, k)
        elif t < mc + 0.7:
            cx, cy = 560, 520
        elif t < ms - 0.9:
            k = ease((t - mc - 0.7) / max(0.3, ms - 0.9 - mc - 0.7)); cx, cy = 560, lerp(520, 960, k)
        else:
            k = eout((t - ms + 0.9) / 0.9); cx, cy = lerp(560, 744, k), 960
        cane(c, cx, cy, t, 1)
    if t > PH["map_cross"] + 0.3:
        c.text(900, 470, "멈춤!", 44, RED, ease((t - PH["map_cross"] - 0.3) / 0.2), stroke=2)
    if t > PH["map_stair"] + 0.3:
        c.text(300, 1145, "계단 앞도 멈춤!", 36, RED, ease((t - PH["map_stair"] - 0.3) / 0.2), stroke=2)
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


# ---------------------------------------------------------------- 3. 과태료 50만 원
def fine(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 50-C  |  블록 위에 물건을 두면")
    a0 = ease(t / 0.2)
    ts = 120
    for i in range(7):
        tile(c, 540, 1080 - i * ts, ts - 10, a0, "line", lift=0.6)
    # 킥보드 아이콘 (블록 위를 가로막음)
    kx, ky = 540, 700
    c.line([(kx - 170, ky + 40), (kx + 150, ky + 40)], (210, 216, 228), 16, a0)
    c.line([(kx + 140, ky + 40), (kx + 110, ky - 170)], (210, 216, 228), 12, a0)
    c.line([(kx + 70, ky - 170), (kx + 150, ky - 170)], (210, 216, 228), 12, a0)
    c.circle(kx - 160, ky + 62, 30, fill=(40, 46, 60), outline=(210, 216, 228), w=6, a=a0)
    c.circle(kx + 140, ky + 62, 30, fill=(40, 46, 60), outline=(210, 216, 228), w=6, a=a0)
    xk = ease((t - 0.4) / 0.25)
    if xk > 0:
        c.line([(kx - 220, ky - 220), (kx + 220, ky + 160)], RED, 14, xk)
        c.line([(kx - 220, ky + 160), (kx + 220, ky - 220)], RED, 14, xk)
    sk = (t - 0.9) / 0.25
    if sk > 0:
        s = 1.6 - 0.6 * eout(min(sk, 1))
        cx, cy = 540, 400
        c.rrect((cx - 300 * s, cy - 90 * s, cx + 300 * s, cy + 90 * s), 26 * s, fill=(60, 14, 16), outline=RED, w=10 * s, a=min(1, sk * 2))
        c.text(cx, cy - 26 * s, "과태료", 40 * s, (255, 200, 195), min(1, sk * 2))
        c.text(cx, cy + 30 * s, "50만 원", 80 * s, RED, min(1, sk * 2), stroke=3)
        if sk < 1.6:
            c.circle(cx, cy, 160 + 300 * eout(min(sk, 1)), outline=(255, 255, 255), w=6, a=max(0, 1 - sk) * 0.8)
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


SCENES = {"blocks": blocks, "map": map_, "fine": fine}
if __name__ == "__main__":
    fn = SCENES[sys.argv[1]]; out = sys.argv[2]
    if out.endswith(".jpg"):
        ims = [fn(float(v)).resize((360, 640), Image.LANCZOS) for v in sys.argv[3:]]
        s = Image.new("RGB", (360 * len(ims), 640)); [s.paste(m, (i * 360, 0)) for i, m in enumerate(ims)]
        s.save(out, quality=86); raise SystemExit
    D = float(sys.argv[3]); tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(D * FPS))):
        p.stdin.write(fn(n / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, out); print("ok", out)
