"""40편 전기장판 설계도 모션그래픽 5장면 — bp30v2 품질 기준(2배 그리기·글로우·둥근 상자 글자).
bars: 난방기기 화재 10년 막대그래프 / xray: 장판 속 열선 스캔 + 접힌 자국 / fold: 접히면 열선 꺾임 → 열 집중 /
layers: 두꺼운 이불 여러 겹 → 열 갇힘 / roll: 접기 ✕ vs 말기 ○
사실: 소방청(2020) 최근 10년 난방기기 화재 8,544건 중 전기장판 2,443건(28.6%)·전기히터 2,186건(25.6%)·나무난로 1,444건(16.9%) ·
한국화재보험협회·소비자원: 접어서 사용·보관 금지(열선 손상·과열) · 행정안전부: 전선·플러그 균열·변색·탄 자국 시 사용 중단 ·
소비자원·소방청 지침: 두꺼운 이불 여러 겹은 위험 요인
usage: python3 bp40.py <scene> out.mp4 dur | out.jpg t1 t2 ..."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image
from bp30v2 import (W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back,
                    LINE, CYAN, YEL, HOT, COLD, ORANGE)

GREEN = (90, 220, 130); WIRE = (255, 140, 50); BEIGE = (214, 196, 160); DIM = (70, 110, 150)

def lerp(a, b, k): return a + (b - a) * k
def mix(c1, c2, k): return tuple(int(lerp(a, b, k)) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- A. 막대그래프
BARS = [("전기장판", 2443, "28.6%"), ("전기히터", 2186, "25.6%"), ("나무난로", 1444, "16.9%")]
def bars(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 40-A  |  난방기기 화재 10년 (소방청)")
    X = [250, 540, 830]; Y0 = 1090; HMAX = 560; BW = 190
    ga = ease((t - 0.05) / 0.3)
    for v in (0, 1000, 2000):                               # 눈금
        y = Y0 - HMAX * v / 2443
        c.line([(110, y), (970, y)], DIM, 2, ga * 0.5)
        c.text(100, y, f"{v:,}", 26, DIM, ga * 0.8, anchor="rm")
    c.line([(110, Y0), (970, Y0)], LINE, 4, ga)
    for i, ((name, v, pct), x) in enumerate(zip(BARS, X)):
        k = eout((t - 0.2 - 0.18 * i) / 0.9); h = HMAX * v / 2443 * k
        win = i == 0
        col = HOT if win else CYAN
        if h > 2:
            c.rrect((x - BW / 2, Y0 - h, x + BW / 2, Y0), 18, fill=mix(col, (8, 26, 56), 0.35), outline=col, w=4, a=0.95 if win else 0.7)
            if h > 40: c.rrect((x - BW / 2 + 16, Y0 - h + 14, x - BW / 2 + 34, Y0 - 14), 9, fill=(255, 255, 255), a=0.22)
        n = int(v * k)
        c.text(x, Y0 - h - 44, f"{n:,}건", 46 if win else 40, YEL if win else LINE, ease((t - 0.25 - 0.18 * i) / 0.2), stroke=3)
        c.text(x, Y0 + 46, name, 42, LINE if not win else YEL, ga, stroke=3)
        if t > 1.35:                                        # 비율
            c.text(x, Y0 - h / 2, pct, 40, (255, 255, 255), ease((t - 1.35 - 0.08 * i) / 0.2), stroke=3)
    if t > 1.15:                                            # 1위 배지
        k = back((t - 1.15) / 0.35); x = X[0]; y = Y0 - HMAX - 150
        c.circle(x, y, 58 * k, fill=HOT, a=1)
        c.circle(x, y, 58 * k, outline=(255, 230, 200), w=5, a=1)
        c.text(x, y - 2, "1위", 44 * k, (255, 255, 255), 1)
        for j in range(2):
            ph = (t * 1.2 + j * 0.5) % 1
            c.circle(x, y, 60 + 70 * ph, outline=HOT, w=3, a=(1 - ph) * 0.8)
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

# ---------------------------------------------------------------- B. 엑스레이 스캔
BX0, BX1, BY0, BY1 = 170, 910, 420, 1100
def wire_path():
    pts = []; rows = 9; m = 46
    for r in range(rows):
        y = BY0 + 50 + r * (BY1 - BY0 - 100) / (rows - 1)
        xs = (BX0 + m, BX1 - m) if r % 2 == 0 else (BX1 - m, BX0 + m)
        pts += [(xs[0], y), (xs[1], y)]
    return pts
WPATH = wire_path()
FOLD_Y = (BY0 + BY1) / 2

def blanket_top(c, a, quilt=True):
    c.rrect((BX0, BY0, BX1, BY1), 40, fill=(30, 52, 86), outline=LINE, w=5, a=a)
    if quilt:
        for x in np.arange(BX0 + 92, BX1 - 40, 92):
            c.line([(x, BY0 + 12), (x, BY1 - 12)], LINE, 2, a * 0.18)
        for y in np.arange(BY0 + 85, BY1 - 40, 85):
            c.line([(BX0 + 12, y), (BX1 - 12, y)], LINE, 2, a * 0.18)
    # 전선 + 조절기
    c.line([(BX1 - 30, BY1 - 40), (BX1 + 40, BY1 + 30), (BX1 + 40, BY1 + 90)], LINE, 6, a)
    c.rrect((BX1 - 10, BY1 + 90, BX1 + 90, BY1 + 150), 14, fill=(220, 226, 236), a=a)

def xray(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 40-B  |  전기장판 속을 들여다보면")
    a = ease((t - 0.05) / 0.3)
    blanket_top(c, a)
    sy = lerp(BY0 - 20, BY1 + 20, ease((t - 0.2) / 0.75))   # 스캔선
    vis = []
    for p, q in zip(WPATH[:-1], WPATH[1:]):                  # 스캔선 위쪽만 열선 보이기
        if p[1] <= sy and q[1] <= sy: vis.append((p, q))
        elif p[1] <= sy < q[1]:
            k = (sy - p[1]) / (q[1] - p[1]); vis.append((p, (lerp(p[0], q[0], k), sy)))
    for p, q in vis:
        c.line([p, q], WIRE, 7, 0.95)
    for i in range(1, len(WPATH) - 1, 2):                    # 굽이: 반원
        p, q = WPATH[i], WPATH[i + 1]
        cyy = (p[1] + q[1]) / 2; rr = (q[1] - p[1]) / 2; side = 1 if p[0] > 540 else -1
        arc = [(p[0] + side * rr * math.cos(a), cyy + rr * math.sin(a)) for a in np.linspace(-math.pi / 2, math.pi / 2, 20)]
        arc = [pt for pt in arc if pt[1] <= sy]
        if len(arc) > 1: c.line(arc, WIRE, 7, 0.95)
    if 0.15 < t < 1.0:
        c.line([(BX0 - 30, sy), (BX1 + 30, sy)], CYAN, 6, 0.9)
        c.rrect((BX0 - 30, sy - 26, BX1 + 30, sy), 0, fill=CYAN, a=0.10)
    if t > 0.7:
        c.text(540, BY0 - 50, "열선", 40, WIRE, ease((t - 0.7) / 0.2), stroke=3)
    if t > 1.0:                                              # 접힌 자국
        k = eout((t - 1.0) / 0.3); x1 = lerp(BX0, BX1, k)
        pul = 0.75 + 0.25 * math.sin(t * 10)
        for x in np.arange(BX0, x1, 34):
            c.line([(x, FOLD_Y), (min(x + 20, x1), FOLD_Y)], YEL, 8, pul)
        callout(c, W / 2, 1200, "접힌 자국", 64, YEL, ease((t - 1.2) / 0.12), 0.7 + 0.3 * back((t - 1.2) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

# ---------------------------------------------------------------- C. 접히면 열선이 꺾이고 열이 몰림
HX, HY = 560, 860; HALF = 400; TH = 22
def rot(px, py, ang):
    ca, sa = math.cos(ang), math.sin(ang)
    dx, dy = px - HX, py - (HY - TH)
    return HX + dx * ca - dy * sa, (HY - TH) + dx * sa + dy * ca
def fold(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 40-C  |  접힌 곳의 단면")
    a0 = ease((t - 0.05) / 0.3)
    ang = -math.pi * 0.985 * ease((t - 0.25) / 0.9)          # 오른쪽 반이 위로 접혀 올라감
    # 바닥
    c.line([(90, HY + TH + 4), (990, HY + TH + 4)], DIM, 3, a0 * 0.7)
    # 왼쪽 반(고정)
    c.rrect((HX - HALF, HY - TH, HX, HY + TH), TH, fill=BEIGE, a=a0 * 0.85)
    c.line([(HX - HALF + 14, HY), (HX, HY)], WIRE, 5, a0)
    # 오른쪽 반(회전)
    corners = [(HX, HY - TH), (HX + HALF, HY - TH), (HX + HALF, HY + TH), (HX, HY + TH)]
    c.poly([rot(x, y, ang) for x, y in corners], BEIGE, a0 * 0.85)
    wire_r = [rot(x, HY, ang) for x in np.linspace(HX, HX + HALF - 14, 20)]
    c.line(wire_r, WIRE, 5, a0)
    # 접힌 곳 둥근 이음
    c.circle(HX, HY - TH * (1 - math.cos(ang)) / 2, TH * (0.6 + 0.4 * abs(math.sin(ang / 2))), fill=BEIGE, a=a0 * 0.85)
    kink = ease((t - 0.9) / 0.3)
    # 열 몰림
    heat = ease((t - 1.15) / 0.9)
    if heat > 0:
        fl = 1 + 0.08 * math.sin(t * 23) + 0.05 * math.sin(t * 37)
        for r, al in ((150, 0.10), (100, 0.18), (62, 0.32), (34, 0.6)):
            c.circle(HX, HY - TH, r * fl * (0.5 + 0.5 * heat), fill=mix(ORANGE, HOT, r / 150), a=al * heat)
        for i in range(5):                                   # 올라가는 열기
            ph = (t * 1.1 + i * 0.2) % 1; x0 = HX - 60 + i * 30
            pts = [(x0 + 10 * math.sin(s / 14 + t * 6 + i), HY - 60 - s - ph * 120) for s in range(0, 120, 6)]
            c.line(pts, HOT, 4, heat * (1 - ph) * 0.8)
    # 돋보기 확대 (꺾인 열선)
    if t > 0.85:
        ia = ease((t - 0.85) / 0.25); cx, cy, R = 780, 520, 150
        c.line([(HX + 20, HY - 40), (cx - R * 0.75, cy + R * 0.7)], LINE, 3, ia * 0.7)
        c.circle(cx, cy, R, fill=(10, 30, 62), outline=LINE, w=5, a=ia * 0.95)
        v = 70 * kink
        c.line([(cx - 110, cy - 50 - v * 0.2), (cx, cy + 40), (cx + 110, cy - 50 - v * 0.2)], WIRE, 10, ia)
        c.line([(cx - 110, cy - 50 - v * 0.2), (cx, cy + 40), (cx + 110, cy - 50 - v * 0.2)], mix(WIRE, HOT, heat), 10, ia * heat)
        if kink > 0.5:
            c.text(cx, cy + 100, "꺾임!", 40, HOT, ease((t - 1.05) / 0.15), stroke=3)
    if t > 1.75:
        callout(c, W / 2, 1180, "열이 한곳에!", 66, HOT, ease((t - 1.75) / 0.12), 0.7 + 0.3 * back((t - 1.75) / 0.3))
    return intro_fade(c.compose(base, glow=0.9), t).convert("RGB")

# ---------------------------------------------------------------- D. 이불 여러 겹 → 열 갇힘
def layers(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 40-D  |  이불을 여러 겹 덮으면")
    a0 = ease((t - 0.05) / 0.3); X0, X1, FY = 140, 760, 1080
    c.line([(90, FY), (990, FY)], DIM, 3, a0 * 0.7)
    c.rrect((X0, FY - 30, X1, FY - 4), 12, fill=mix(BEIGE, ORANGE, 0.4), outline=WIRE, w=3, a=a0)
    c.text((X0 + X1) / 2, FY + 40, "전기장판", 36, LINE, a0, stroke=3)
    LH = 70; tops = []
    cols = [(120, 150, 210), (150, 120, 190), (110, 170, 160)]
    heat = ease((t - 0.9) / 1.4); ceil = FY - 30 - LH * 3 + 10
    for i in range(3):                                       # 이불이 한 장씩 떨어짐
        td = 0.25 + 0.38 * i; k = back((t - td) / 0.35) if t > td else 0
        if k <= 0: continue
        yb = FY - 30 - LH * i; y = lerp(yb - 420, yb, min(1, k)) + (k - 1) * 30
        c.rrect((X0 - 20, y - LH + 6, X1 + 20, y), 26, fill=mix(cols[i], HOT, heat * 0.35), outline=LINE, w=3, a=0.9)
        for x in np.arange(X0 + 40, X1, 90):
            c.line([(x, y - LH + 18), (x, y - 10)], LINE, 2, 0.2)
        tops.append(y - LH)
    if heat > 0:                                             # 위로 못 빠져나가고 안에서 맴도는 열
        for i in range(7):
            x = X0 + 40 + i * 100; ph = (t * 0.9 + i * 0.17) % 1
            y = lerp(FY - 44, ceil + 30, math.sin(math.pi * ph))
            c.circle(x + 12 * math.sin(t * 5 + i), y, 13, fill=mix(ORANGE, HOT, heat), a=heat * 0.9)
            c.arrow(x, y - 18, x, y - 46, (255, 230, 200), 4, 12, heat * 0.6 * (1 if ph < 0.5 else 0))
        c.line([(X0 - 30, ceil - 2), (X1 + 30, ceil - 2)], HOT, 6, heat * (0.6 + 0.4 * math.sin(t * 9)))
    # 온도계
    tx, ty0, ty1 = 900, 1060, 500
    c.rrect((tx - 26, ty1 - 20, tx + 26, ty0), 26, fill=(10, 30, 62), outline=LINE, w=4, a=a0)
    c.circle(tx, ty0 + 18, 44, fill=(10, 30, 62), outline=LINE, w=4, a=a0)
    lv = 0.18 + 0.78 * heat; col = mix(ORANGE, HOT, heat)
    c.rrect((tx - 14, lerp(ty0, ty1, lv), tx + 14, ty0 + 10), 14, fill=col, a=a0)
    c.circle(tx, ty0 + 18, 32, fill=col, a=a0)
    for k_ in range(6):
        y = lerp(ty0 - 30, ty1 + 10, k_ / 5); c.line([(tx + 30, y), (tx + 48, y)], LINE, 3, a0 * 0.7)
    if t > 1.95:
        callout(c, W / 2, 1190, "열이 갇혀요!", 66, HOT, ease((t - 1.95) / 0.12), 0.7 + 0.3 * back((t - 1.95) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

# ---------------------------------------------------------------- E. 접기 ✕ vs 말기 ○
def roll(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 40-E  |  보관할 때")
    a0 = ease((t - 0.05) / 0.3); Y = 990
    c.line([(540, 380), (540, 1110)], DIM, 3, a0 * 0.6)
    c.text(290, 440, "접기", 60, LINE, a0, stroke=4); c.text(790, 440, "말기", 60, LINE, a0, stroke=4)
    # 왼쪽: 지그재그로 접힘
    p = ease((t - 0.3) / 1.0); n = 6; L = 420 / n; ang = math.radians(68) * p
    x, y = 80, Y; pts = [(x, y)]
    for i in range(n):
        s_ = 1 if i % 2 == 0 else -1
        x += L * math.cos(ang); y += -s_ * L * math.sin(ang)
        pts.append((x, y))
    sh = 290 - (pts[0][0] + pts[-1][0]) / 2
    pts = [(q[0] + sh * p, q[1]) for q in pts]
    c.line(pts, BEIGE, 34, a0)
    c.line(pts, WIRE, 6, a0)
    for q in pts[1:-1]:
        c.circle(q[0], q[1], 12, fill=HOT, a=p * (0.6 + 0.4 * math.sin(t * 12)))
    # 오른쪽: 돌돌 말림
    pr = ease((t - 0.3) / 1.0); x0, x1 = 590, 1000; r0 = 10
    r = r0 + 70 * math.sqrt(pr) + 17; cx = lerp(x0 + 20, x0 + 230, pr); cy = Y - r
    c.line([(cx, Y), (x1 - (x1 - x0 - 250) * pr, Y)], BEIGE, 34, a0)
    c.line([(cx, Y), (x1 - (x1 - x0 - 250) * pr, Y)], WIRE, 6, a0)
    tmax = max(0.2, 0.2 + 3.2 * pr) * 2 * math.pi
    sp = []
    for th in np.linspace(0, tmax, 160):
        rho = r0 + (r - r0) * th / tmax; ph = th - tmax + math.pi / 2
        sp.append((cx + rho * math.cos(ph), cy + rho * math.sin(ph)))
    c.line(sp, BEIGE, 20, a0)
    c.line(sp, WIRE, 4, a0 * 0.9)
    # 판정 도장
    if t > 1.45:
        k = back((t - 1.45) / 0.3)
        c.line([(290 - 95 * k, 640 - 95 * k), (290 + 95 * k, 640 + 95 * k)], HOT, 20, 1)
        c.line([(290 + 95 * k, 640 - 95 * k), (290 - 95 * k, 640 + 95 * k)], HOT, 20, 1)
    if t > 1.7:
        k = back((t - 1.7) / 0.3)
        c.circle(790, 640, 100 * k, outline=GREEN, w=20, a=1)
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- A v2. 전문 인포그래픽형 순위 막대
TOTAL = 8544
ROWS = [("전기장판", 2443, 28.6, HOT), ("전기히터", 2186, 25.6, CYAN), ("나무난로", 1444, 16.9, (120, 200, 190))]
BG_N = (12, 34, 70)
def eexpo(x): x = max(0.0, min(1.0, x)); return 1 - 2 ** (-10 * x) if x < 1 else 1.0

def icon(c, kind, x, y, a, hot=False):
    s = 34
    c.rrect((x - s - 8, y - s - 8, x + s + 8, y + s + 8), 18, fill=(16, 44, 86), outline=mix(LINE, BG_N, 0.4), w=2, a=a)
    if kind == 0:                                            # 전기장판: 패드 + 지그재그 열선
        c.rrect((x - s + 2, y - s + 10, x + s - 2, y + s - 10), 8, fill=BEIGE, a=a)
        pts = []
        for i in range(5):
            yy = y - s + 18 + i * 9
            pts += [(x - s + 10, yy), (x + s - 10, yy)] if i % 2 == 0 else [(x + s - 10, yy), (x - s + 10, yy)]
        c.line(pts, WIRE if not hot else (255, 90, 40), 3, a)
    elif kind == 1:                                          # 전기히터: 몸체 + 빛나는 봉 3개
        c.rrect((x - s + 6, y - s + 4, x + s - 6, y + s - 12), 8, fill=(200, 210, 225), a=a)
        for i in range(3):
            xx = x - 16 + i * 16
            c.rrect((xx - 4, y - s + 12, xx + 4, y + s - 20), 4, fill=ORANGE, a=a)
        c.rrect((x - 22, y + s - 12, x + 22, y + s - 4), 4, fill=(150, 160, 180), a=a)
    else:                                                    # 나무난로: 몸체 + 연통 + 불꽃
        c.rrect((x - s + 8, y - 10, x + s - 8, y + s - 6), 6, fill=(90, 100, 118), a=a)
        c.rrect((x + 6, y - s + 2, x + 16, y - 10), 2, fill=(90, 100, 118), a=a)
        c.poly([(x - 10, y + 18), (x - 2, y - 2), (x + 6, y + 18)], ORANGE, a)
        c.poly([(x - 6, y + 18), (x - 2, y + 8), (x + 2, y + 18)], YEL, a)

def bars(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 40-A  |  난방기기 화재 · 최근 10년 (소방청)")
    BX0, BXMAX = 300, 900; BH_ = 76; YS = [650, 830, 1010]
    # 헤더: 총 건수 카운터
    ha = ease((t - 0.05) / 0.3)
    c.text(540, 360, "난방기기 화재 10년 합계", 36, mix(LINE, BG_N, 0.25), ha)
    n = int(TOTAL * eexpo((t - 0.15) / 1.0))
    c.text(540, 445, f"{n:,}건", 92, LINE, ha, stroke=4)
    c.line([(380, 506), (700, 506)], CYAN, 3, ha * 0.6)
    # 눈금선
    for v in (0, 1000, 2000):
        x = BX0 + (BXMAX - BX0) * v / 2443
        c.line([(x, 560), (x, 1075)], mix(DIM, BG_N, 0.35), 2, ha * 0.7)
        c.text(x, 1100, f"{v:,}", 26, DIM, ha * 0.9)
    focus = ease((t - 1.45) / 0.3)                            # 1위 강조 단계
    for i, ((name, v, pct, col), y) in enumerate(zip(ROWS, YS)):
        lead = i == 0
        ra = ease((t - 0.25 - 0.08 * i) / 0.25)
        dx = (1 - eout((t - 0.25 - 0.08 * i) / 0.35)) * -60
        dim = 0 if lead else 0.55 * focus
        colr = mix(col, BG_N, dim)
        # 순위 배지 + 아이콘 + 이름
        bk = max(0.05, back((t - 0.3 - 0.08 * i) / 0.3))
        c.circle(70 + dx, y, 30 * bk, fill=mix(HOT if lead else (60, 90, 140), BG_N, dim), a=ra)
        c.text(70 + dx, y - 1, str(i + 1), 36 * bk, (255, 255, 255), ra)
        icon(c, i, 168 + dx, y, ra * (1 - dim * 0.6), hot=lead and focus > 0)
        c.text(BX0 + dx, y - BH_ / 2 - 30, name, 46, mix(YEL if lead else LINE, BG_N, dim), ra, anchor="lm", stroke=3)
        # 막대 (부드럽게 감속하며 자람)
        k = eexpo((t - 0.45 - 0.12 * i) / 0.9)
        L = (BXMAX - BX0) * v / 2443 * k
        if L > BH_ / 2:
            x1 = BX0 + dx + L
            c.rrect((BX0 + dx, y - BH_ / 2, x1, y + BH_ / 2), BH_ / 2, fill=mix(colr, BG_N, 0.25), a=ra)
            c.rrect((BX0 + dx + 4, y - BH_ / 2 + 4, x1 - 4, y + 2), BH_ / 2 - 6, fill=mix(colr, (255, 255, 255), 0.18), a=ra)
            c.rrect((x1 - BH_ + 6, y - BH_ / 2 + 6, x1 - 6, y + BH_ / 2 - 6), BH_ / 2 - 6, fill=mix(colr, (255, 255, 255), 0.45), a=ra)
            if lead and focus > 0:                           # 빛이 쓱 지나감 (가늘고 은은하게)
                ph = ((t - 1.5) * 0.9) % 1.2
                sx = BX0 + dx + (L + 160) * ph - 80
                for w_, mk in ((26, 0.12), (12, 0.22), (4, 0.34)):
                    xa, xb = sx - w_, sx + w_
                    if xa > BX0 + dx + 30 and xb < x1 - 40:
                        c.rrect((xa, y - BH_ / 2 + 10, xb, y + BH_ / 2 - 10), 6, fill=mix(colr, (255, 255, 255), mk), a=ra)
            # 값 (막대와 함께 올라가는 숫자)
            nv = int(v * k)
            tx = min(x1 + 18, 1000)
            if lead:
                c.text(x1 - 26, y, f"{pct * k:.1f}%", 38, (255, 255, 255), ra * ease((t - 1.0) / 0.2), anchor="rm")
            c.text(x1 + 16, y - 1, f"{nv:,}", 46 if lead else 38, mix(YEL if lead else LINE, BG_N, dim), ra, anchor="lm", stroke=3)
    # 1위 강조: 둘레 빛 + 왕관 배지
    if focus > 0:
        y = YS[0]; L = (BXMAX - BX0)
        pul = 0.5 + 0.5 * math.sin(t * 8)
        c.rrect((BX0 - 14, y - BH_ / 2 - 14, BX0 + L + 14, y + BH_ / 2 + 14), BH_ / 2 + 14, outline=HOT, w=3, a=focus * (0.5 + 0.4 * pul))
        bk = max(0.05, back((t - 1.5) / 0.35))
        bx, by = BX0 + L - 60, y - BH_ / 2 - 46
        c.rrect((bx - 60 * bk, by - 26 * bk, bx + 60 * bk, by + 26 * bk), 26 * bk, fill=HOT, a=focus)
        c.text(bx, by - 2, "1위", 36 * bk, (255, 255, 255), focus)
    # 전체 중 비율 띠
    sa = ease((t - 1.8) / 0.25); SY = 1190; SX0, SX1 = 70, 1010
    if sa > 0:
        c.text(SX0, SY - 44, "전체 화재 중", 30, mix(LINE, BG_N, 0.2), sa, anchor="lm")
        c.rrect((SX0, SY - 22, SX1, SY + 22), 22, fill=(20, 46, 88), a=sa)
        segs = [(28.6, HOT), (25.6, mix(CYAN, BG_N, 0.45)), (16.9, mix((120, 200, 190), BG_N, 0.45))]
        x = SX0
        for j, (p_, col) in enumerate(segs):
            k = eexpo((t - 1.9 - 0.12 * j) / 0.5); w_ = (SX1 - SX0) * p_ / 100 * k
            if w_ > 6:
                c.rrect((x + 2, SY - 18, x + w_ - 2, SY + 18), 18, fill=col, a=sa)
            x += (SX1 - SX0) * p_ / 100
        if t > 2.35:                                         # 대괄호 + '4건 중 1건 넘게'
            ba = ease((t - 2.35) / 0.2); xe = SX0 + (SX1 - SX0) * 0.286
            c.line([(SX0 + 4, SY + 30), (SX0 + 4, SY + 40), (xe - 4, SY + 40), (xe - 4, SY + 30)], YEL, 4, ba)
            c.text((SX0 + xe) / 2 + 170, SY + 4, "← 4건 중 1건 넘게!", 0, YEL, 0) if False else None
            c.text(SX0 + 6, SY + 74, "4건 중 1건 넘게!", 40, YEL, ba, anchor="lm", stroke=3)
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

SCENES = {"bars": bars, "xray": xray, "fold": fold, "layers": layers, "roll": roll}
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
