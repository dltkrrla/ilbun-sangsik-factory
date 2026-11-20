"""16편 리메이크(맥주병은 왜 갈색) 설계도 모션그래픽 5장면 — bp30v2와 같은 품질 기준(2배 그리기·글로우·둥근 상자 글자).
sun: 해에서 자외선·파란 빛이 맥주잔으로 / hop: 홉이 빛을 받으면 성분이 쪼개짐 / scale: 10억분의 1g /
timer: 투명 잔 + 햇빛 30분 → 냄새 / filter: 투명·초록·갈색 유리를 지나는 빛
사실: 일광취 = 빛(파란 빛·자외선, 약 350~500nm)이 홉의 쓴맛 성분을 쪼개 생기는 3-MBT(스컹크 냄새와 비슷) ·
한 병(12온스)에 10억분의 1g만 있어도 느끼는 사람이 있음, 투명 잔 + 햇빛 창가 30분 → 뚜렷한 이취 (Cook's Illustrated) ·
갈색 유리는 500nm 아래 빛을 막음, 초록·투명은 거의 못 막음 (Science News, Craft Beer & Brewing)
usage: python3 bp16.py <scene> out.mp4 dur | prev.jpg t1 t2 ..."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image
from bp30v2 import (W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back,
                    LINE, CYAN, YEL, HOT, COLD, ORANGE)

VIOLET = (170, 120, 255); BLUE = (90, 150, 255); AMBER = (200, 120, 40); BEER = (240, 180, 60); GREEN = (90, 200, 120)
SUN_C = (255, 214, 90)

def sun_draw(c, x, y, r, t, a=1.0):
    for i in range(14):                                   # 빙글 도는 햇살
        th = t * 0.6 + i * 2 * math.pi / 14
        c.line([(x + (r + 14) * math.cos(th), y + (r + 14) * math.sin(th)), (x + (r + 46) * math.cos(th), y + (r + 46) * math.sin(th))], SUN_C, 6, a)
    c.circle(x, y, r, fill=SUN_C, a=a)
    c.circle(x, y, r * 0.72, fill=(255, 238, 160), a=a)

def pint(c, x, y, h, a=1.0, fill=1.0, col=BEER, t=0.0):
    """투명한 맥주잔 (바닥 가운데 x, y)."""
    wt, wb = h * 0.36, h * 0.28
    pts = [(x - wt, y - h), (x - wb, y), (x + wb, y), (x + wt, y - h)]
    if fill > 0:                                          # 맥주 + 거품
        top = y - h * 0.86 * fill
        k = (y - top) / h
        lt = wb + (wt - wb) * (1 - (y - top) / h * 0 ) * k if False else wb + (wt - wb) * ((y - top) / h)
        c.poly([(x - lt + 6, top), (x - wb + 6, y - 6), (x + wb - 6, y - 6), (x + lt - 6, top)], col, a * 0.85)
        c.rrect((x - lt + 6, top - h * 0.08, x + lt - 6, top + 4), 14, fill=(255, 248, 230), a=a * 0.95)
        for i in range(7):                                # 거품 방울
            ph = (t * 0.7 + i * 0.37) % 1.0
            bx = x + (i - 3) * wb * 0.22; by = y - 14 - ph * (y - top - 30)
            c.circle(bx, by, 4, outline=(255, 255, 255), w=2, a=a * 0.7)
    c.line(pts, LINE, 6, a)
    c.line([(x - wt + 16, y - h + 30), (x - wb + 14, y - 30)], (255, 255, 255), 4, a * 0.35)

def bottle(c, x, y, h, col=AMBER, a=1.0, outline=LINE):
    """라벨 없는 맥주병 실루엣 (바닥 가운데 x, y)."""
    w = h * 0.2; nk = h * 0.07
    pts = [(x - nk, y - h), (x - nk, y - h * 0.72), (x - w, y - h * 0.5), (x - w, y), (x + w, y), (x + w, y - h * 0.5), (x + nk, y - h * 0.72), (x + nk, y - h)]
    c.poly(pts, col, a * 0.55)
    c.line(pts + [pts[0]], outline, 6, a)
    c.rrect((x - nk - 6, y - h - 18, x + nk + 6, y - h + 4), 6, fill=(200, 200, 210), a=a)

def wave_ray(c, x0, y0, x1, y1, col, t, a=1.0, amp=10, lam=46, w=5, head=True):
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    pts = []
    for s in np.arange(0, L, 4):
        o = amp * math.sin(2 * math.pi * s / lam - t * 12)
        pts.append((x0 + ux * s + nx * o, y0 + uy * s + ny * o))
    c.line(pts, col, w, a)
    if head: c.arrow(x1 - ux * 30, y1 - uy * 30, x1, y1, col, w, 20, a)

# ---------------------------------------------------------------
SPEC = [(380, (130, 60, 220)), (430, (80, 90, 255)), (480, (40, 180, 255)), (530, (60, 220, 90)), (580, (250, 230, 40)), (630, (255, 140, 30)), (700, (230, 40, 40))]
def spec_col(nm):
    for (a0, c0), (a1, c1) in zip(SPEC, SPEC[1:]):
        if a0 <= nm <= a1:
            g = (nm - a0) / (a1 - a0); return tuple(int(c0[k] * (1 - g) + c1[k] * g) for k in range(3))
    return SPEC[0][1] if nm < 380 else SPEC[-1][1]

def spectrum_bar(c, x0, y, w, t, a):
    """빛의 색 막대 (350~700nm) + 범인 구간(350~500nm) 강조."""
    for i in range(int(w)):
        nm = 350 + 350 * i / w
        c.line([(x0 + i, y - 18), (x0 + i, y + 18)], spec_col(nm), 1.3, a)
    c.text(x0 - 14, y, "자외선", 26, VIOLET, a, anchor="rm"); c.text(x0 + w + 14, y, "빨강", 26, HOT, a, anchor="lm")
    k = ease((t - 1.0) / 0.3)
    if k > 0:
        xb = x0 + w * (150 / 350)
        c.rrect((x0 - 6, y - 30, x0 + (xb - x0) * k + 6, y + 30), 10, outline=YEL, w=5, a=k)
        c.text((x0 + xb) / 2, y + 62, "이 빛이 범인", 34, YEL, k, stroke=3)

def sun(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 16-A  |  햇빛 속의 빛")
    spectrum_bar(c, 200, 350, 680, t, ease((t - 0.2) / 0.3))
    sun_draw(c, 830, 610, 120 * eout(t / 0.4) + 1, t, ease(t / 0.3))
    pint(c, 330, 1190, 540, a=ease((t - 0.1) / 0.3), t=t)
    for i, col in enumerate((VIOLET, BLUE, VIOLET, BLUE, VIOLET)):
        k = eout((t - 0.3 - i * 0.07) / 0.5)
        if k > 0:
            x0, y0 = 740 - i * 14, 690 + i * 22; x1, y1 = 470 - i * 34, 820 + i * 70
            wave_ray(c, x0, y0, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k, col, t, a=0.95, amp=14, w=7)
    if t > 0.95:
        callout(c, 700, 1240, "자외선 · 파란 빛", 54, VIOLET, ease((t - 0.95) / 0.12), 0.7 + 0.3 * back((t - 0.95) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

def bract(c, x, y, w, h, a, shade):
    pts = []
    for k in range(25):
        u = k / 24; yy = y - h / 2 + h * u
        half = w * math.sin(math.pi * u) ** 0.8 * (1 - 0.45 * u)
        pts.append((x - half, yy))
    pts += [(2 * x - px, py) for px, py in reversed(pts)]
    base_col = (int(70 + 60 * shade), int(150 + 60 * shade), int(80 + 40 * shade))
    c.poly(pts, base_col, a)
    c.line(pts + [pts[0]], (190, 245, 170), 3, a)
    c.line([(x, y - h / 2 + 10), (x, y + h / 2 - 14)], (150, 220, 140), 2, a * 0.7)

def hop_cone(c, x, y, s, a):
    c.line([(x, y - 250 * s), (x + 40 * s, y - 330 * s)], GREEN, 7, a)        # 줄기
    for r in range(7):                                    # 위에서 아래로 비늘이 겹친 솔방울 모양
        n = 3 if r % 2 == 0 else 2
        wdt = (1 - abs(r - 3) / 4.6) * 66 * s
        for q in range(n):
            ox = (q - (n - 1) / 2) * 64 * s * (1 - abs(r - 3) / 6)
            bract(c, x + ox, y + (r - 3) * 62 * s, wdt * 0.9, 110 * s, a, 0.2 + 0.8 * (q == (n - 1) // 2))

def molecule(c, x, y, sc, t, split, a):
    atoms = [(-150, 0), (-90, -40), (-30, 0), (30, -40), (90, 0), (150, -40)]
    for i in range(len(atoms) - 1):
        (ax, ay), (bx, by) = atoms[i], atoms[i + 1]
        if i == 2 and split > 0: continue
        off = (1 if i > 2 else -1) * 50 * split
        c.line([(x + (ax + (off if i >= 3 else (off if i < 2 else 0))) * sc, y + ay * sc), (x + (bx + (off if i >= 2 else off)) * sc, y + by * sc)], LINE, 5, a)
    for i, (ax, ay) in enumerate(atoms):
        off = (50 if i >= 3 else -50) * split
        c.circle(x + (ax + off) * sc, y + ay * sc, 18 * sc, fill=(GREEN if i < 3 else ORANGE), a=a)
    if split > 0:
        k = split
        for j in range(8):                                # 쪼개지는 불꽃
            th = j * math.pi / 4
            c.line([(x + 30 * k * math.cos(th), y - 20 + 30 * k * math.sin(th)), (x + 60 * k * math.cos(th), y - 20 + 60 * k * math.sin(th))], YEL, 4, a * (1 - k * 0.6))

def hop(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 16-B  |  홉 — 맥주의 쓴맛")
    a = ease(t / 0.35)
    hop_cone(c, 290, 760, 1.15 * eout(t / 0.5) + 0.01, a)
    c.text(290, 1110, "홉 (쓴맛)", 48, GREEN, ease((t - 0.3) / 0.3), stroke=3)
    sun_draw(c, 930, 400, 60, t, a)
    k = eout((t - 0.7) / 0.5)
    if k > 0: wave_ray(c, 900, 450, 900 + (760 - 900) * k, 450 + (850 - 450) * k, VIOLET, t, a=0.95, amp=14, w=7)
    if t > 0.9:
        ma = ease((t - 0.9) / 0.3); sp = eout((t - 1.6) / 0.5)
        molecule(c, 740, 900, 1.25, t, sp, ma)
        c.text(740, 1010, "쓴맛 성분", 40, LINE, ma * (1 - sp), stroke=3)
    if t > 1.9:
        callout(c, W / 2, 1220, "빛을 받으면 쪼개져요", 52, YEL, ease((t - 1.9) / 0.12), 0.7 + 0.3 * back((t - 1.9) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

def scale(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 16-C  |  얼마나 조금이면 냄새가 날까")
    z = 1 + 14 * ease((t - 0.7) / 1.6) ** 2               # 병 속으로 확 줌인
    cx, cy = 540, 760
    if z < 9:
        a = 1 - ease((z - 5) / 4)
        bottle(c, cx, cy + 360 * z ** 0.15, 680 * min(z, 3) ** 0.6, a=a)
        c.text(cx, cy + 420, "맥주 한 병", 40, LINE, a * (1 - ease((t - 0.7) / 0.3)), stroke=3)
    # 줌인할수록 나타나는 눈금 원
    for i in range(6):
        r = (80 + i * 90) * (z / 3) % 520
        c.circle(cx, cy, r, outline=CYAN, w=2, a=ease((t - 0.8) / 0.4) * 0.35)
    if t > 1.9:                                           # 마지막에 남는 아주 작은 점
        k = back((t - 1.9) / 0.4)
        c.circle(cx, cy, 10 * k, fill=YEL, a=1)
        for i in range(2):
            ph = ((t * 1.4 + i * 0.5) % 1.0)
            c.circle(cx, cy, 20 + 70 * ph, outline=YEL, w=3, a=1 - ph)
    s = "0.000 000 001 g"; n = int(len(s) * ease((t - 0.3) / 1.6))
    c.text(cx, 420, s[:n], 72, LINE, ease((t - 0.3) / 0.2), stroke=4)
    if t > 2.2:
        callout(c, W / 2, 1180, "10억분의 1g", 70, YEL, ease((t - 2.2) / 0.12), 0.7 + 0.3 * back((t - 2.2) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

def timer(t):
    base = BG.copy(); c = Canvas(); title(c, t, "실험  |  투명 잔 + 햇빛 창가")
    a = ease(t / 0.3)
    sun_draw(c, 860, 420, 70, t, a)
    c.line([(110, 1080), (970, 1080)], LINE, 5, a)          # 창틀
    pint(c, 330, 1075, 430, a=a, t=t)
    for i in range(3):
        wave_ray(c, 800 - i * 20, 490 + i * 20, 470 - i * 30, 760 + i * 60, (VIOLET, BLUE, VIOLET)[i], t, a=0.75 * a, head=False)
    # 시계: 0 → 30분
    k = ease((t - 0.4) / 2.0); gx, gy, gr = 760, 830, 130
    c.circle(gx, gy, gr, outline=LINE, w=6, a=a)
    c.d.pieslice([(gx - gr + 14) * 2, (gy - gr + 14) * 2, (gx + gr - 14) * 2, (gy + gr - 14) * 2], -90, -90 + 360 * k,
                 fill=(255, 212, 70, int(170 * a)))
    th = math.radians(-90 + 360 * k)
    c.line([(gx, gy), (gx + (gr - 30) * math.cos(th), gy + (gr - 30) * math.sin(th))], LINE, 6, a)
    c.text(gx, gy + gr + 50, f"{int(30 * k)}분", 56, YEL, a, stroke=4)
    # 냄새 물결
    sm = ease((t - 1.6) / 0.8)
    if sm > 0:
        for i in range(3):
            pts = []
            for j in range(40):
                yy = 620 - j * 9; ph = t * 4 + j * 0.35 + i * 2
                pts.append((300 + (i - 1) * 50 + 16 * math.sin(ph), yy - ((t * 60) % 30)))
            c.line(pts, GREEN, 6, sm * 0.9)
    if t > 2.6:
        callout(c, W / 2, 1230, "30분 만에 맛이 변해요", 52, GREEN, ease((t - 2.6) / 0.12), 0.7 + 0.3 * back((t - 2.6) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

def filt(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 16-D  |  유리 색에 따라 지나가는 빛")
    a = ease(t / 0.3)
    rows = [("투명", (215, 238, 255), 1.0), ("초록", GREEN, 0.85), ("갈색", AMBER, 0.1)]
    for i, (name, col, passk) in enumerate(rows):
        y = 520 + i * 290
        c.rrect((450, y - 100, 560, y + 100), 18, fill=col, outline=LINE, w=5, a=a * 0.92)
        c.rrect((466, y - 86, 480, y + 56), 7, fill=(255, 255, 255), a=a * 0.35)
        c.text(505, y - 132, name + " 유리", 40, col if name != "투명" else LINE, a, stroke=3)
        k = eout((t - 0.15 - i * 0.1) / 0.55)
        if k > 0: wave_ray(c, 90, y, 90 + (440 - 90) * k, y, VIOLET, t, a=0.95, amp=16, w=8, head=False)
        k2 = eout((t - 0.75 - i * 0.1) / 0.55)
        if k2 > 0 and passk > 0.3:
            wave_ray(c, 570, y, 570 + (990 - 570) * k2, y, VIOLET, t, a=0.95 * passk, amp=16 * passk, w=8)
        if name == "갈색":
            if k2 > 0: wave_ray(c, 570, y, 570 + 70 * k2, y, VIOLET, t, a=0.35, amp=3, w=5, head=False)
            if t > 1.15:
                kk = back((t - 1.15) / 0.3)
                c.text(800, y, "막았다!", int(60 * (0.6 + 0.4 * kk)), YEL, ease((t - 1.15) / 0.12), stroke=5)
    if t > 1.6:
        callout(c, W / 2, 1288, "갈색 유리가 빛을 막아요", 52, ORANGE, ease((t - 1.6) / 0.12), 0.7 + 0.3 * back((t - 1.6) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

SCENES = {"sun": sun, "hop": hop, "scale": scale, "timer": timer, "filter": filt}
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
