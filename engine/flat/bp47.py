"""47편 손소독제(노로바이러스) 설계도 모션그래픽 5장면 — bp40 품질 기준.
shell: 알코올 방울이 노로바이러스 단단한 껍질에 튕겨 나감(일반 균은 터짐) / soap: 비누 분자가 손 위 바이러스를 감싸 물에 씻어 냄(30초) /
door: 문고리 위 바이러스가 사흘 동안 살아 있음 / bleach: 락스 1 : 물 50 / heat: 굴 85℃ 1분 넘게 익히기
사실: 질병관리청(2025-01-07 보도자료·2023-11-30 정책브리핑) — 손 소독제보다 비누로 30초 이상 손 씻기 · 일상 환경에서 사흘간 생존 ·
락스 1 : 물 50 희석액으로 오염 물품 소독 · 식재료 85℃ 이상에서 1분 이상 익히기 / Penn State Health 2025: 알코올 손소독제는 노로바이러스에 효과 낮음 /
TODAY(NBC) 2025: 단단한 겉껍질 때문
usage: python3 bp47.py <scene> out.mp4 dur | out.jpg t1 t2 ..."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image
from bp30v2 import (W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back,
                    LINE, CYAN, YEL, HOT, COLD, ORANGE)
from bp40 import lerp, mix, GREEN, DIM, BG_N

VIR = (130, 222, 96); VIR_D = (58, 120, 52); SHELL = (40, 90, 46); ALC = (120, 210, 255); SOAPC = (255, 170, 210); SKIN = (222, 178, 140)


def virus(c, x, y, r, a=1.0, t=0.0, shell=1.0, spikes=12):
    """노로바이러스: 둥근 몸 + 돌기 + (선택) 단단한 이중 껍질."""
    for i in range(spikes):
        ang = i * 2 * math.pi / spikes + 0.12 * math.sin(t * 2 + i)
        x1, y1 = x + r * 1.0 * math.cos(ang), y + r * 1.0 * math.sin(ang)
        x2, y2 = x + r * 1.28 * math.cos(ang), y + r * 1.28 * math.sin(ang)
        c.line([(x1, y1), (x2, y2)], VIR_D, max(3, r * 0.07), a)
        c.circle(x2, y2, r * 0.1, fill=VIR, a=a)
    for k in range(6, 0, -1):                                  # 둥근 입체감 (안쪽 밝게)
        kk = k / 6
        c.circle(x - r * 0.12 * (1 - kk), y - r * 0.12 * (1 - kk), r * (0.35 + 0.65 * kk), fill=mix((190, 248, 150), VIR_D, kk ** 0.8), a=a)
    if shell > 0:
        c.circle(x, y, r * 1.0, outline=(30, 70, 36), w=max(4, r * 0.15 * shell), a=a * shell)
        c.circle(x, y, r * 0.84, outline=(110, 180, 90), w=max(2, r * 0.03), a=a * shell * 0.8)
        for j in range(16):                                    # 껍질 알갱이
            ang = j * 2 * math.pi / 16
            c.circle(x + r * 0.92 * math.cos(ang), y + r * 0.92 * math.sin(ang), r * 0.045, fill=(190, 240, 170), a=a * shell)
    c.circle(x - r * 0.3, y - r * 0.32, r * 0.14, fill=(255, 255, 255), a=a * 0.35)


def xmark(c, x, y, s, col=HOT, a=1.0, w=9):
    c.line([(x - s, y - s), (x + s, y + s)], col, w, a); c.line([(x - s, y + s), (x + s, y - s)], col, w, a)


def card(c, x0, y0, x1, y1, a, col=DIM, fill=(10, 30, 62)):
    c.rrect((x0, y0, x1, y1), 28, fill=fill, outline=col, w=3, a=a * 0.92)


def drop(c, x, y, s, a=1.0, col=ALC):
    c.poly([(x, y - 46 * s), (x + 22 * s, y + 4 * s), (x - 22 * s, y + 4 * s)], col, a)
    c.circle(x, y + 8 * s, 24 * s, fill=col, a=a)
    c.circle(x - 8 * s, y + 2 * s, 7 * s, fill=(255, 255, 255), a=a * 0.6)


# ---------------------------------------------------------------- 1. 알코올이 껍질에 튕김
def shell(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 47-A  |  노로바이러스 vs 알코올")
    a0 = ease(t / 0.25); vx, vy, R = 540, 700, 215
    sh = ease((t - 0.2) / 0.7)
    for rr_, al in ((R * 1.75, 0.05), (R * 1.5, 0.07)):                       # 은은한 후광
        c.circle(vx, vy, rr_, fill=(40, 120, 70), a=al * a0)
    virus(c, vx, vy, R, a0, t, shell=sh, spikes=14)
    if t > 0.55:
        ka = ease((t - 0.55) / 0.2)
        c.line([(vx + R * 0.7, vy - R * 0.7), (vx + 300, vy - 330)], YEL, 3, ka)
        callout(c, vx + 270, vy - 370, "단단한 껍질", 42, YEL, ka, 0.75 + 0.25 * back((t - 0.55) / 0.3))
    # 알코올 병(위, 가운데): 방울이 위에서 떨어져 껍질에 맞고 튕김
    c.rrect((540 - 80, 330, 540 + 80, 410), 20, fill=(28, 60, 100), outline=ALC, w=4, a=a0)
    c.rrect((540 - 44, 296, 540 + 44, 332), 10, fill=(180, 210, 240), a=a0)
    c.text(540, 372, "알코올", 36, ALC, a0)
    hits = [(0.8, -150), (1.05, 10), (1.3, 150), (1.55, -70), (1.8, 90)]
    for i, (th, dx) in enumerate(hits):
        k = (t - th) / 0.38
        sx = vx + dx; ytop = 420; ys = vy - math.sqrt(max(1, (R * 1.02) ** 2 - dx * dx)) - 10
        if 0 <= k < 1:
            drop(c, sx, lerp(ytop, ys, ease(k) ** 1.2), 1.1)
        elif 1 <= k < 2.6:
            kk = (k - 1) / 1.6; ang = -math.pi / 2 + (0.9 if dx >= 0 else -0.9) * (1 + 0.4 * (i % 2))
            for m in range(5):
                px = sx + 300 * kk * math.cos(ang + 0.35 * (m - 2)); py = ys + 300 * kk * math.sin(ang + 0.35 * (m - 2)) + 420 * kk * kk
                c.circle(px, py, 12 * (1 - kk) + 3, fill=ALC, a=(1 - kk) * 0.9)
            c.circle(sx, ys, 30 + 80 * kk, outline=(255, 255, 255), w=5, a=(1 - kk) * 0.75)
            if kk < 0.4:
                xmark(c, sx, ys - 46, 24, HOT, 1 - kk / 0.4)
    # 아래 비교 카드 2장
    cy0, cy1 = 990, 1195
    pa = ease((t - 0.3) / 0.3)
    card(c, 70, cy0, 510, cy1, pa * a0, col=(150, 130, 230)); card(c, 570, cy0, 1010, cy1, pa * a0, col=VIR_D)
    gx, gy, gr = 290, 1080, 56
    gk = (t - 1.3) / 0.35
    if gk < 1:
        wob = 1 + 0.04 * math.sin(t * 9)
        c.circle(gx, gy, gr * wob, fill=(170, 150, 230), outline=(110, 90, 190), w=3, a=a0)
        c.circle(gx - 18, gy - 18, 12, fill=(255, 255, 255), a=0.35 * a0)
        if gk > 0:
            drop(c, gx, lerp(gy - 190, gy - gr, ease(gk)), 0.8)
    else:
        pk = (t - 1.65) / 0.5
        if pk < 1:
            c.circle(gx, gy, gr + 110 * eout(pk), outline=(255, 255, 255), w=5, a=(1 - pk) * 0.9)
            for m in range(10):
                ang = m * 0.628; rd = gr + 80 * eout(pk)
                c.circle(gx + rd * math.cos(ang), gy + rd * math.sin(ang), 11 * (1 - pk) + 3, fill=(190, 170, 250), a=1 - pk)
        else:
            xmark(c, gx, gy, 36, HOT, 0.95)
    c.text(290, 1166, "일반 균 → 터짐", 34, (200, 185, 250), a0)
    vk = ease((t - 1.5) / 0.3)
    virus(c, 790, 1080, 40 + 0, a0, t, shell=sh, spikes=10)
    if t > 1.55:
        for i_ in range(3):
            kk = ((t - 1.55 - 0.18 * i_) % 0.55) / 0.55
            drop(c, 790 + (-30 + 30 * i_), 1000 + 50 * kk, 0.45, (1 - kk) * 0.8)
    c.text(790, 1166, "노로바이러스 → 버팀", 34, VIR, a0)
    if t > 2.1:
        callout(c, W / 2, 1255, "알코올이 안 통해요!", 62, HOT, ease((t - 2.1) / 0.12), 0.7 + 0.3 * back((t - 2.1) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- 2. 비누 분자가 감싸서 물에 씻어 냄 (30초)
def soap_mol(c, x, y, ang, a, col=SOAPC):
    tx, ty = x + 34 * math.cos(ang), y + 34 * math.sin(ang)
    nx, ny = -math.sin(ang), math.cos(ang)
    zz = [(tx + 8 * math.sin(i * 2.2) * nx + (i * 8) * math.cos(ang), ty + 8 * math.sin(i * 2.2) * ny + (i * 8) * math.sin(ang)) for i in range(4)]
    c.line([(x, y)] + [(tx, ty)] + zz, (255, 224, 242), 4, a * 0.95)
    c.circle(x, y, 14, fill=col, a=a); c.circle(x - 4, y - 4, 4, fill=(255, 255, 255), a=a * 0.7)


def soap(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 47-B  |  비누 30초 (손 표면 확대)")
    a0 = ease(t / 0.25)
    ys = lambda x: 1090 + 16 * math.sin(x * 0.028) + 9 * math.sin(x * 0.1)
    pts = [(x, ys(x)) for x in range(-10, 1100, 10)]
    c.poly(pts + [(1090, 1500), (-10, 1500)], (176, 120, 96), a0)                         # 진피(아래층)
    c.poly([(x, y + 56 + 10 * math.sin(x * 0.02)) for x, y in pts] + [(1090, 1500), (-10, 1500)], (140, 88, 76), a0)
    c.poly(pts + [(x, y + 52) for x, y in reversed(pts)], (232, 186, 150), a0)             # 표피
    for j in range(9):                                                                     # 지문 골
        xx = 60 + j * 120
        c.line([(xx + 18 * math.sin(i * 0.5), ys(xx) + 10 + i * 4) for i in range(11)], (196, 142, 110), 4, a0 * 0.8)
    c.line(pts, (255, 232, 200), 6, a0)
    flow = ease((t - 1.5) / 1.0)
    for i, vx0 in enumerate([240, 430, 640, 840]):
        vx = vx0 + 1000 * flow * (1.0 + 0.1 * i) * (flow > 0)
        lift = ease((t - 1.0 - 0.1 * i) / 0.6)
        vy = ys(vx0) - 54 - 90 * lift - 24 * math.sin(t * 3 + i) * lift
        if vx < 1260:
            virus(c, vx, vy, 46, a0, t + i, shell=0.0, spikes=10)
            wrap = ease((t - 0.7 - 0.12 * i) / 0.45)
            if wrap > 0:
                for m in range(10):
                    ang = m * 2 * math.pi / 10 + t * 0.5
                    soap_mol(c, vx + 88 * math.cos(ang), vy + 88 * math.sin(ang), ang + math.pi, a0 * wrap)
    if t > 1.3:
        wa = ease((t - 1.3) / 0.3) * 0.75
        for j in range(6):
            yy = 880 + 30 * j
            c.line([(x, yy + 16 * math.sin((x - 340 * t) * 0.016 + j)) for x in range(0, 1081, 12)], (110, 190, 255), 6, wa * (1 - 0.1 * j))
        c.arrow(120, 800, 300, 800, ALC, 8, 28, wa)
        c.text(330, 800, "흐르는 물", 32, ALC, wa, anchor="lm")
    cx, cy, rr = 540, 520, 175
    c.circle(cx, cy, rr, outline=DIM, w=16, a=a0 * 0.8)
    prog = ease((t - 0.3) / 2.0); n = 48
    for k in range(int(n * prog)):
        a1 = -math.pi / 2 + k * 2 * math.pi / n; a2 = -math.pi / 2 + (k + 1.15) * 2 * math.pi / n
        c.line([(cx + rr * math.cos(a1), cy + rr * math.sin(a1)), (cx + rr * math.cos(a2), cy + rr * math.sin(a2))], YEL if prog < 1 else GREEN, 18, 1)
    c.text(cx, cy - 8, f"{int(30 * prog)}", 130, YEL if prog < 1 else GREEN, a0, stroke=4)
    c.text(cx, cy + 90, "초", 42, LINE, a0)
    if t > 2.3:
        callout(c, W / 2, 1255, "비누로 30초 넘게!", 62, GREEN, ease((t - 2.3) / 0.12), 0.7 + 0.3 * back((t - 2.3) / 0.3))
    c.text(70, 1170, "비누 분자가 바이러스를 감싸서 물에 씻겨 가요", 30, LINE, a0 * 0.9, anchor="lm")
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


# ---------------------------------------------------------------- 3. 문고리 위 바이러스, 사흘
def door(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 47-C  |  문고리 위 바이러스 (옆면)")
    a0 = ease(t / 0.25)
    # 문(왼쪽 옆면) + 문고리판 + 목 + 둥근 손잡이
    c.rrect((60, 320, 250, 930), 14, fill=(84, 110, 140), outline=(150, 180, 210), w=3, a=a0)
    c.rrect((250, 560, 290, 740), 10, fill=(176, 132, 60), outline=(240, 200, 120), w=3, a=a0)
    c.rrect((290, 630, 470, 670), 10, fill=(150, 110, 46), outline=(240, 200, 120), w=3, a=a0)
    kx, ky, R = 660, 650, 205
    for k in range(8, 0, -1):
        kk = k / 8
        c.circle(kx - R * 0.16 * (1 - kk), ky - R * 0.16 * (1 - kk), R * (0.3 + 0.7 * kk), fill=mix((255, 236, 160), (140, 98, 36), kk ** 0.9), a=a0)
    c.circle(kx - R * 0.35, ky - R * 0.38, R * 0.14, fill=(255, 255, 255), a=a0 * 0.55)
    pts = [(-0.55, -0.55), (0.05, -0.78), (0.62, -0.35), (-0.78, 0.05), (0.3, 0.3), (-0.2, 0.6), (0.75, 0.5), (-0.35, -0.12)]
    for i, (px, py) in enumerate(pts):
        puls = 1 + 0.12 * math.sin(t * 7 + i * 1.7)
        virus(c, kx + R * px, ky + R * py, 26 * puls, a0 * ease((t - 0.2 - 0.05 * i) / 0.2), t + i, shell=0.0, spikes=8)
    for d in range(3):                                          # 사흘 달력
        bx = 200 + 340 * d; by = 1060
        on = (t - 0.3) / 0.75 >= d
        col = YEL if on else DIM
        pk = back((t - 0.3 - 0.75 * d) / 0.3) if on else 0.0
        c.rrect((bx - 130, by - 90, bx + 130, by + 90), 22, fill=(14, 36, 70), outline=col, w=4 if on else 2, a=a0 * (1 if on else 0.55))
        c.rrect((bx - 130, by - 90, bx + 130, by - 34), 22, fill=col if on else DIM, a=a0 * (0.95 if on else 0.4))
        c.text(bx, by - 62, f"{d + 1}일째", 34, (10, 30, 60) if on else LINE, a0)
        if on:
            virus(c, bx, by + 26, 30 * max(pk, 0.05), 1.0, t + d, shell=0.0, spikes=8)
    if t > 2.1:
        callout(c, W / 2, 1255, "문고리에서도 사흘!", 62, YEL, ease((t - 2.1) / 0.12), 0.7 + 0.3 * back((t - 2.1) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


# ---------------------------------------------------------------- 4. 락스 1 : 물 50
def bleach(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 47-D  |  락스 희석 (오염 물품 닦기)")
    a0 = ease(t / 0.25)
    # 양동이 (사다리꼴) + 물 채워짐
    bx0, bx1, by0, by1 = 330, 750, 580, 940
    lvl = ease((t - 0.8) / 1.5)
    top_l, top_r, bot_l, bot_r = bx0, bx1, bx0 + 50, bx1 - 50
    c.poly([(top_l, by0), (top_r, by0), (bot_r, by1), (bot_l, by1)], (16, 44, 84), a0)
    wy = by1 - (by1 - by0) * 0.88 * lvl
    f_ = (by1 - wy) / (by1 - by0)
    wl = bot_l + (top_l - bot_l) * f_; wr = bot_r + (top_r - bot_r) * f_
    if lvl > 0:
        c.poly([(wl, wy), (wr, wy), (bot_r, by1), (bot_l, by1)], mix(COLD, (8, 26, 56), 0.35), a0)
        c.line([(wl + (wr - wl) * q / 20, wy + 6 * math.sin(q * 1.3 + t * 5)) for q in range(21)], (190, 230, 255), 4, a0 * 0.9)
    c.line([(top_l, by0), (bot_l, by1), (bot_r, by1), (top_r, by0)], LINE, 6, a0)
    c.arrow(540, 520, 540, 520, LINE, 1, 1, 0)
    for m in range(1, 6):                                                                   # 눈금
        yy = by1 - (by1 - by0) * 0.88 * m / 5
        c.line([(top_r - (top_r - bot_r) * (1 - (by1 - yy) / (by1 - by0)) - 40, yy), (top_r - (top_r - bot_r) * (1 - (by1 - yy) / (by1 - by0)), yy)], DIM, 3, a0)
    # 노란 락스 한 방울(1) — 위에서 떨어져 퍼짐
    dk = (t - 0.25) / 0.5
    if 0 <= dk < 1:
        drop(c, 540, lerp(420, wy if lvl > 0 else 760, ease(dk)), 1.2, 1, col=YEL)
    if t > 0.25:
        c.rrect((540 - 120, 330, 540 + 120, 410), 22, fill=(70, 60, 10), outline=YEL, w=5, a=a0)
        c.text(540, 370, "락스  1", 56, YEL, a0, stroke=3)
    # 눈금띠: 노랑 1칸 + 파랑 50칸 (한 줄, 51칸)
    n_on = int(50 * ease((t - 0.8) / 1.6))
    x0, cw = 40, 20; yb = 1020
    c.rrect((x0, yb, x0 + cw - 2, yb + 70), 4, fill=YEL, a=a0 * back((t - 0.3) / 0.3))
    for n in range(50):
        xx = x0 + cw * (n + 1)
        if n < n_on:
            c.rrect((xx, yb, xx + cw - 2, yb + 70), 4, fill=mix(COLD, (8, 26, 56), 0.2), a=0.95)
        else:
            c.rrect((xx, yb, xx + cw - 2, yb + 70), 4, outline=DIM, w=1, a=a0 * 0.4)
    c.text(x0 + 10, yb - 28, "1", 36, YEL, a0, anchor="mm", stroke=2)
    c.text(540, yb + 112, "물 50", 50, ALC, a0 * ease((t - 0.8) / 0.3), stroke=3)
    if t > 2.5:
        callout(c, W / 2, 1255, "락스 1 : 물 50", 64, YEL, ease((t - 2.5) / 0.12), 0.7 + 0.3 * back((t - 2.5) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


# ---------------------------------------------------------------- 5. 굴 85℃ 1분
def oyster(c, x, y, s, a):
    n = 28
    out = [(x + 190 * s * (1 + 0.05 * math.sin(7 * q)) * math.cos(q), y + 120 * s * (1 + 0.05 * math.sin(7 * q)) * math.sin(q)) for q in [i * 2 * math.pi / n for i in range(n)]]
    c.poly(out, (120, 112, 96), a)
    inn = [(x + 166 * s * math.cos(q), y + 98 * s * math.sin(q)) for q in [i * 2 * math.pi / n for i in range(n)]]
    c.poly(inn, (238, 228, 208), a)
    for k_ in range(1, 4):
        c.line([(x + 166 * s * math.cos(q) * k_ / 4, y + 98 * s * math.sin(q) * k_ / 4) for q in [i * 2 * math.pi / n for i in range(n + 1)]], (220, 206, 184), 3, a * 0.6)
    c.circle(x - 60 * s, y - 36 * s, 22 * s, fill=(255, 255, 255), a=a * 0.35)


def heat(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 47-E  |  굴 익히기")
    a0 = ease(t / 0.25)
    temp = 20 + 70 * ease((t - 0.3) / 1.4); fr = (temp - 20) / 70
    # 냄비 + 끓는 물
    px0, px1, py0, py1 = 330, 960, 560, 940
    c.rrect((px0, py0, px1, py1), 40, fill=(30, 40, 58), outline=(170, 180, 200), w=6, a=a0)
    c.rrect((px0 + 14, py0 + 70, px1 - 14, py1 - 14), 30, fill=mix((60, 130, 230), (120, 190, 255), fr), a=a0 * 0.85)
    c.line([(px0 + 14 + (px1 - px0 - 28) * q / 24, py0 + 70 + 5 * math.sin(q * 1.4 + t * 6)) for q in range(25)], (230, 245, 255), 5, a0 * 0.9)
    c.rrect((px1, 650, px1 + 70, 690), 14, fill=(90, 100, 120), a=a0); c.rrect((px0 - 70, 650, px0, 690), 14, fill=(90, 100, 120), a=a0)
    rng = np.random.default_rng(5)
    for b in range(14):                                                           # 기포
        k = (t * (0.6 + 0.8 * fr) + rng.uniform()) % 1
        bx = px0 + 40 + rng.uniform() * (px1 - px0 - 80); by = py1 - 60 - (py1 - py0 - 150) * k
        c.circle(bx, by, 6 + 8 * rng.uniform(), outline=(230, 245, 255), w=3, a=a0 * 0.6 * fr)
    for sidx in range(3):                                                         # 김
        sx = 520 + 160 * sidx
        c.line([(sx + 20 * math.sin(q * 0.9 + t * 4 + sidx), py0 - 20 - q * 14) for q in range(9)], (200, 220, 240), 6, a0 * 0.5 * fr)
    ox, oy = 645, 760
    oyster(c, ox, oy, 1.1, a0)
    for i, (qx, qy) in enumerate([(-90, -25), (-5, -45), (80, -10), (-45, 35), (55, 40)]):
        dead = temp >= 85 and t > 1.7 + 0.05 * i
        life = 1 - ease((t - 1.7 - 0.05 * i) / 0.3) if temp >= 85 else 1
        if life > 0.01:
            virus(c, ox + qx, oy + qy, 22, a0 * life, t + i, shell=0.0, spikes=8)
        if dead and t < 2.3 + 0.05 * i:
            xmark(c, ox + qx, oy + qy, 22, HOT, 1 - ease((t - 2.0 - 0.05 * i) / 0.3))
    tx, ty0, ty1 = 200, 1060, 420
    c.rrect((tx - 36, ty1 - 20, tx + 36, ty0 + 20), 36, fill=(10, 30, 60), outline=LINE, w=4, a=a0)
    hy = ty0 - (ty0 - ty1) * fr
    col = mix(COLD, HOT, fr)
    c.rrect((tx - 20, hy, tx + 20, ty0), 20, fill=col, a=a0)
    c.circle(tx, ty0 + 24, 50, fill=col, outline=LINE, w=4, a=a0)
    y85 = ty0 - (ty0 - ty1) * (65 / 70)
    c.line([(tx + 44, y85), (tx + 150, y85)], YEL, 4, a0)
    c.text(tx + 160, y85, "85℃", 42, YEL, a0, anchor="lm", stroke=3)
    c.text(tx, ty1 - 58, f"{int(temp)}℃", 48, mix(LINE, YEL, fr), a0, stroke=3)
    cx, cy, rr = 645, 1050, 100
    c.circle(cx, cy, rr, outline=DIM, w=14, a=a0 * 0.8)
    pr = ease((t - 1.8) / 1.0)
    for k_ in range(int(40 * pr)):
        a1 = -math.pi / 2 + k_ * 2 * math.pi / 40; a2 = -math.pi / 2 + (k_ + 1.15) * 2 * math.pi / 40
        c.line([(cx + rr * math.cos(a1), cy + rr * math.sin(a1)), (cx + rr * math.cos(a2), cy + rr * math.sin(a2))], GREEN, 16, 1)
    c.text(cx, cy - 4, "1분", 52, LINE if pr < 1 else GREEN, a0 * (0.5 + 0.5 * pr), stroke=3)
    if t > 2.9:
        callout(c, W / 2, 1255, "85℃에서 1분 넘게!", 60, YEL, ease((t - 2.9) / 0.12), 0.7 + 0.3 * back((t - 2.9) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


SCENES = {"shell": shell, "soap": soap, "door": door, "bleach": bleach, "heat": heat}
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
