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


# ---------- 16-C v2: 병 속으로 파고드는 줌 → 분자들 사이 단 하나의 '범인' ----------
from PIL import ImageDraw as _ID
def _bez(p0, p1, p2, p3, n=18):
    return [((1-u)**3*p0[0]+3*(1-u)**2*u*p1[0]+3*(1-u)*u*u*p2[0]+u**3*p3[0],
             (1-u)**3*p0[1]+3*(1-u)**2*u*p1[1]+3*(1-u)*u*u*p2[1]+u**3*p3[1]) for u in np.linspace(0, 1, n)]
BH = 640; BW = BH * 0.2; NK = BH * 0.066
def _bottle_path():
    """병 오른쪽 반 윤곽(바닥 가운데 = 0,0, 위쪽이 -y) → 좌우 대칭으로 이어 붙임."""
    r = [(NK, -BH), (NK, -BH * 0.70)]
    r += _bez((NK, -BH * 0.70), (NK, -BH * 0.58), (BW, -BH * 0.58), (BW, -BH * 0.45))[1:]
    r += [(BW, -BH * 0.05)]
    r += _bez((BW, -BH * 0.05), (BW, -BH * 0.01), (BW * 0.9, 0), (BW * 0.78, 0), 8)[1:]
    l = [(-x, y) for x, y in reversed(r)]
    return r + l
BPATH = _bottle_path()
LIQ = -BH * 0.74                                          # 맥주 높이(목 아래쪽)
FOC = (0.0, -BH * 0.24)                                   # 줌이 파고드는 곳 = '범인' 분자 자리
_rng = np.random.default_rng(16)
BUB = [(_rng.uniform(-0.85, 0.85) * BW, _rng.uniform(-0.44, -0.03) * BH, _rng.uniform(1.2, 4.5), _rng.uniform(0, 1)) for _ in range(70)]
MOL_SP = 118                                              # 마지막 화면에서 분자 간격(px)
_g = np.arange(-34, 35)
MOL = [(i * MOL_SP + _rng.uniform(-40, 40), j * MOL_SP * 0.92 + _rng.uniform(-40, 40), _rng.uniform(15, 24), _rng.uniform(0, 6.28))
       for i in _g for j in _g if not (i == 0 and j == 0)]
MOL = [m + (int(_rng.integers(1, 4)),) for m in MOL]
_g2 = np.arange(-40, 41)
MOL2 = [(i * 76 + _rng.uniform(-30, 30), j * 70 + _rng.uniform(-30, 30), _rng.uniform(7, 11), _rng.uniform(0, 6.28)) for i in _g2 for j in _g2]
BOKEH = [(_rng.uniform(0, 6.28), _rng.uniform(0, 1), _rng.uniform(70, 150)) for _ in range(9)]
def _radial(col, a0, rad, power=1.6):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    return lambda cx, cy, a: None
_YY, _XX = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
def _glow_img(cx, cy, a):
    d = np.sqrt((_XX * 4 - cx) ** 2 + ((_YY * 4 - cy) / 1.1) ** 2) / 620
    al = np.clip(1 - d, 0, 1) ** 1.8 * 150 * a
    arr = np.zeros((H // 4, W // 4, 4), np.uint8); arr[..., 0] = 255; arr[..., 1] = 205; arr[..., 2] = 110; arr[..., 3] = al.astype(np.uint8)
    return Image.fromarray(arr, "RGBA").resize((W, H), Image.BILINEAR)
_d = np.sqrt(((_XX * 4 - W / 2) / (W * 0.62)) ** 2 + ((_YY * 4 - H * 0.42) / (H * 0.55)) ** 2)
_v = np.zeros((H // 4, W // 4, 4), np.uint8); _v[..., 0] = 14; _v[..., 1] = 8; _v[..., 2] = 4
_v[..., 3] = (np.clip(_d - 0.45, 0, 1) ** 1.3 * 255).clip(0, 235).astype(np.uint8)
VIGN = Image.fromarray(_v, "RGBA").resize((W, H), Image.BILINEAR)
def _atom(c, x, y, r, base, hi, a, w):
    c.circle(x, y, r, fill=base, outline=hi, w=w, a=a)
    c.circle(x - r * 0.32, y - r * 0.34, r * 0.3, fill=(255, 246, 225), a=a * 0.75)
AMB_D, AMB_L = np.array([120, 58, 12], np.float32), np.array([235, 150, 55], np.float32)

def _zoom(t):
    k = ease((t - 0.75) / 1.65); k = k ** 1.6
    return math.exp(math.log(420) * k)

def _focus_screen(t):
    k = ease((t - 0.6) / 1.4)
    return 540, 905 + (760 - 905) * k

def _xf(t):
    z = _zoom(t); fx, fy = _focus_screen(t)
    return z, (lambda x, y: (fx + (x - FOC[0]) * z, fy + (y - FOC[1]) * z))

def _liquid_layer(t, a):
    """병 속 맥주: 가로 그러데이션(가장자리 진하게) + 빛 줄기. 1배 크기로 그림."""
    z, P = _xf(t)
    m = Image.new("L", (W, H), 0); d = _ID.Draw(m)
    pts = [P(x, max(y, LIQ)) for x, y in BPATH]
    d.polygon(pts, fill=255)
    cx = P(0, 0)[0]; half = BW * z
    u = np.clip(np.abs(np.arange(W, dtype=np.float32) - cx) / max(half, 1), 0, 1)
    shade = (1 - u ** 2.2)[None, :, None]
    col = AMB_D + (AMB_L - AMB_D) * shade
    vy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    col = col * (0.92 + 0.12 * (1 - vy))
    arr = np.zeros((H, W, 4), np.float32); arr[..., :3] = col
    arr[..., 3] = np.array(m, np.float32) * 0.62 * a
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

def _odometer(c, t, y=400, size=84):
    s = "0.000 000 001 g"; f = F(size); total = f.getlength(s); x0 = W / 2 - total / 2
    for i, ch in enumerate(s):
        ti = 0.30 + 0.075 * i
        if t < ti or ch == " ": continue
        cw = f.getlength(ch); x = x0 + f.getlength(s[:i]) + cw / 2
        settle = ti + 0.22; a = ease((t - ti) / 0.08)
        if ch.isdigit() and t < settle:
            shown = str(int((t - ti) * 46 + i * 3) % 10); dy = 10 * math.sin((t - ti) * 60)
            c.text(x, y + dy, shown, size, LINE, a * 0.55, stroke=4)
            continue
        is_one = (ch == "1")
        sc = 1.0 + (0.35 * (1 - back((t - settle) / 0.3)) if is_one else 0)
        col = YEL if is_one else (CYAN if ch == "g" else LINE)
        c.text(x, y, ch, size * sc, col, a, stroke=4)

def scale(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 16-C  |  얼마나 조금이면 냄새가 날까")
    z, P = _xf(t)
    # 1) 맥주(그러데이션) — 병이 화면을 덮어도 계속 깔림
    fill_a = ease((t - 0.25) / 0.45)
    base.alpha_composite(_liquid_layer(t, fill_a))
    # 2) 병 윤곽: 그려지듯 나타남 → 줌에 따라 화면 밖으로
    if z < 60:
        pts = [P(x, y) for x, y in BPATH]
        L = np.cumsum([0] + [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)])
        k = eout(t / 0.55) * L[-1]; part = [p for p, l in zip(pts, L) if l <= k]
        oa = 1 - ease((z - 25) / 35)
        c.line(part, LINE, 6, oa)
        cap = (P(-NK - 7, -BH - 20), P(NK + 7, -BH + 4))
        c.rrect((cap[0][0], cap[0][1], cap[1][0], cap[1][1]), 8 * min(z, 4), fill=(190, 196, 210), a=oa * ease((t - 0.45) / 0.2))
        hl = [P(-BW * 0.66, -BH * 0.43), P(-BW * 0.66, -BH * 0.08)]          # 유리 반사광
        c.line(hl, (255, 255, 255), 9 * z, oa * 0.28 * fill_a)
        sx, sy = P(0, LIQ)
        c.line([P(-NK + 3, LIQ), P(NK - 3, LIQ)], (255, 244, 220), 4, oa * fill_a * 0.9)
        la = fill_a * (1 - ease((t - 0.75) / 0.25))
        c.text(540, P(0, 0)[1] + 60, "맥주 한 병", 44, LINE, la, stroke=3)
    # 3) 탄산 방울: 줌인하면 옆으로 커지며 스쳐 지나감
    for (bx, by, br, ph) in BUB:
        yy = by - ((t * 26 + ph * 200) % (BH * 0.4)) * 0.3
        if yy < LIQ: continue
        x, y = P(bx, yy); r = br * z
        if r > 420 or r < 1 or not (-r < x < W + r and -r < y < H + r): continue
        a = fill_a * 0.85 * (1 - ease((r - 160) / 260))
        c.circle(x, y, r, outline=(255, 240, 210), w=max(2, min(6, r * 0.12)), a=a * 0.8)
        c.circle(x - r * 0.35, y - r * 0.35, r * 0.18, fill=(255, 255, 255), a=a * 0.7)
    # 4) 빠르게 파고드는 속도선
    sp = ease((t - 1.0) / 0.4) * (1 - ease((t - 2.05) / 0.3))
    if sp > 0:
        fx, fy = _focus_screen(t)
        for i in range(36):
            ang = i * 2 * math.pi / 36 + (i % 3) * 0.05
            ph = (t * 2.6 + i * 0.137) % 1.0
            r0 = 160 + ph * 900; r1 = r0 + 90 + 160 * ph
            c.line([(fx + r0 * math.cos(ang), fy + r0 * math.sin(ang)), (fx + r1 * math.cos(ang), fy + r1 * math.sin(ang))],
                   LINE, 3, sp * 0.32 * (1 - ph))
    # 5) 분자들 (줌 끝 무렵 나타남) — 뒤층(작고 흐림) + 앞층(원자 2~3개 덩어리) + 가운데 노란 '범인'
    mz = z / 420; ma = ease((math.log(z) - math.log(90)) / (math.log(300) - math.log(90)))
    fx, fy = _focus_screen(t)
    inside = ease((math.log(z) - math.log(8)) / (math.log(40) - math.log(8)))
    if inside > 0:
        base.alpha_composite(Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), _glow_img(fx, fy, 1.0), inside))
    if ma > 0:
        m2 = mz * 0.55
        for (mx, my, mr, ph) in MOL2:
            x = fx + (mx + 4 * math.sin(t * 2 + ph)) * m2; y = fy + (my + 4 * math.cos(t * 2.2 + ph)) * m2
            if not (-20 < x < W + 20 and 240 < y < 1280): continue
            c.circle(x, y, mr * m2, fill=(150, 95, 45), a=ma * 0.45 * (1 - ease((abs(y - 760) - 250) / 260)))
        for (mx, my, mr, ph, na) in MOL:
            x = fx + (mx + 7 * math.sin(t * 3 + ph)) * mz; y = fy + (my + 7 * math.cos(t * 2.6 + ph)) * mz; r = mr * mz
            if not (-80 < x < W + 80 and 240 < y < 1280): continue
            edge = 1 - ease((abs(y - 760) - 250) / 260)
            rot = ph + t * 0.9
            for k_ in range(na):
                ox = math.cos(rot + k_ * 2.1) * r * 0.95 * (na > 1); oy = math.sin(rot + k_ * 2.1) * r * 0.95 * (na > 1)
                _atom(c, x + ox, y + oy, r * (1 if k_ == 0 else 0.78), (120, 70, 30), (255, 214, 150), ma * 0.8 * edge, max(1.5, 2.5 * mz))
        cr = 30 * mz * (1 + 0.07 * math.sin(t * 9)); rot = t * 1.4
        for k_, (dx, dy, rr) in enumerate(((0, 0, 1.0), (1.05, -0.35, 0.7), (-0.6, 0.95, 0.62))):   # 노란 범인 분자
            ca, sa = math.cos(rot), math.sin(rot)
            _atom(c, fx + (dx * ca - dy * sa) * cr, fy + (dx * sa + dy * ca) * cr, cr * rr, YEL, (255, 250, 215), ma, 3)
        for i in range(2):                               # 냄새 퍼지는 고리
            ph = (t * 1.3 + i * 0.5) % 1.0
            c.circle(fx, fy, cr * 1.6 + 20 + 130 * ph, outline=YEL, w=3, a=ma * (1 - ph) * ease((t - 2.4) / 0.2))
    if inside > 0:
        base.alpha_composite(Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 0)), VIGN, inside))
        for (ang, ph, br) in BOKEH:                     # 앞을 스쳐 가는 흐린 방울(깊이감)
            p = (t * 0.45 + ph) % 1.0; rr = 250 + p * 700
            x = fx + rr * math.cos(ang); y = fy + rr * math.sin(ang) * 1.2
            c.circle(x, y, br * (0.7 + p), fill=(255, 225, 170), a=0.035 * inside * math.sin(math.pi * p))
    # 6) 조준 괄호가 '찰칵' 조여들며 고정 + 이름표
    if t > 2.3:
        k = back((t - 2.3) / 0.35); s_ = 230 - 140 * k; a = ease((t - 2.3) / 0.12)
        for sx_, sy_ in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            x0, y0 = fx + sx_ * s_, fy + sy_ * s_
            c.line([(x0, y0 - sy_ * 44), (x0, y0), (x0 - sx_ * 44, y0)], YEL, 7, a)
        tag_a = ease((t - 2.55) / 0.15)
        c.rrect((fx - 150, fy - s_ - 92, fx + 150, fy - s_ - 30), 31, fill=(8, 26, 56), outline=YEL, w=3, a=tag_a * 0.95)
        c.text(fx, fy - s_ - 63, "일광취 성분", 38, YEL, tag_a)
    # 7) 위 숫자(오도미터) + 아래 큰 강조
    c.rrect((120, 340, 960, 462), 30, fill=(6, 20, 44), a=0.55 * ease((t - 0.2) / 0.3))
    _odometer(c, t)
    if t > 2.75:
        callout(c, W / 2, 1150, "10억분의 1g", 74, YEL, ease((t - 2.75) / 0.12), 0.7 + 0.3 * back((t - 2.75) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

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
