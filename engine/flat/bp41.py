"""41편 도어락(허수 기능) 설계도 모션그래픽 5장면 — bp40 품질 기준.
uv: 자외선 빛이 키패드를 쓸면 지문 자국 4곳이 빛남 / perm: 4×3×2×1 = 24가지, 경우의 수 24칸이 채워짐 /
fake: 아무 숫자(회색) + 비밀번호(노랑) 입력 → 자물쇠 열림 / heat: 열화상 지도 — 허수 없이 4곳만 vs 허수 쓰면 전체로 퍼짐 /
manual: 제품마다 방식이 다름(앞에·중간에·자릿수 제한) → 설명서 확인
사실: 위키트리(허수 기능: 비밀번호 앞뒤에 아무 숫자를 더 눌러 지문 자국을 키패드 전체로 분산) ·
에누리 구매가이드(제조사별 허수 입력 방식이 다름: 앞에 / 중간에, 자릿수 제한 있는 제품도 있음) · 4개 숫자 순서 = 4! = 24
예시 비밀번호(2·5·7·9)는 가상의 예시.
usage: python3 bp41.py <scene> out.mp4 dur | out.jpg t1 t2 ..."""
import math, os, subprocess, sys, itertools
import numpy as np
from PIL import Image, ImageFilter
from bp30v2 import (W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back,
                    LINE, CYAN, YEL, HOT, ORANGE)
from bp40 import lerp, mix, eexpo, GREEN, DIM, BG_N

UV = (170, 120, 255); GLASS = (14, 18, 26); KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]
PW = ["2", "5", "7", "9"]                                     # 예시 비밀번호

def key_centers(cx, top, sx, sy):
    return {k: (cx + (i % 3 - 1) * sx, top + (i // 3) * sy) for i, k in enumerate(KEYS)}

def panel(c, cx, y0, y1, w, a, lit=1.0):
    """유리 키패드 몸체: 테두리 금속 + 검은 유리 + 위쪽 반사광."""
    c.rrect((cx - w / 2 - 14, y0 - 14, cx + w / 2 + 14, y1 + 14), 46, fill=(92, 100, 114), a=a)
    c.rrect((cx - w / 2 - 6, y0 - 6, cx + w / 2 + 6, y1 + 6), 40, fill=(150, 158, 172), a=a)
    c.rrect((cx - w / 2, y0, cx + w / 2, y1), 36, fill=GLASS, a=a)
    c.poly([(cx - w / 2 + 20, y0 + 20), (cx + w / 2 - 120, y0 + 20), (cx - w / 2 + 20, y0 + 260)], (34, 40, 54), a)

def digits(c, K, size, a, colmap=None):
    for k, (x, y) in K.items():
        col = (colmap or {}).get(k, (225, 235, 250))
        c.text(x, y, k, size, col, a)

def fprint(c, x, y, s, col, a, seed):
    """지문: 끊긴 타원 고리 여러 겹."""
    rng = np.random.default_rng(seed)
    for i, r in enumerate(np.arange(5, 34, 4.2)):
        a0 = rng.uniform(0, 6.28); span = rng.uniform(4.0, 5.6)
        pts = [(x + r * s * math.cos(t), y + r * s * 1.25 * math.sin(t)) for t in np.linspace(a0, a0 + span, 26)]
        c.line(pts, col, 3.2, a * (1 - i * 0.05))

# ---------------------------------------------------------------- 1. 자외선 스캔
def uv(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 41-A  |  도어락 키패드 (자외선 비추기)")
    a0 = ease(t / 0.25); cx, y0, y1, w = 540, 420, 1150, 500
    K = key_centers(cx, 545, 150, 175)
    panel(c, cx, y0, y1, w, a0)
    lx = lerp(cx - w / 2 - 160, cx + w / 2 + 160, ease((t - 0.2) / 1.0))     # 빛이 왼→오로 지나감
    for k, (x, y) in K.items():
        if k in PW:
            seen = ease((lx - x + 60) / 120)
            c.circle(x, y, 56, fill=mix(GLASS, (90, 150, 220), 0.12 + 0.4 * seen), a=a0)
            fprint(c, x, y, 1.3, mix((60, 70, 90), (225, 250, 255), seen), a0 * (0.45 + 0.55 * seen), seed=ord(k))
    digits(c, K, 58, a0)
    if 0.15 < t < 1.35:                                         # 자외선 손전등 빛
        la = ease((t - 0.15) / 0.15) * (1 - ease((t - 1.2) / 0.15))
        for wdt, al in ((150, 0.05), (90, 0.08), (40, 0.12)):
            c.poly([(lx - wdt, y0 - 30), (lx + wdt, y0 - 30), (lx + wdt * 0.6, y1 + 30), (lx - wdt * 0.6, y1 + 30)], UV, la * al)
        c.line([(lx, y0 - 30), (lx, y1 + 30)], (220, 200, 255), 3, la * 0.8)
        c.rrect((lx - 46, y0 - 110, lx + 46, y0 - 40), 18, fill=(60, 64, 80), a=la)
        c.circle(lx, y0 - 40, 26, fill=UV, a=la)
    if t > 1.3:                                                 # 4곳 표시
        for i, k in enumerate(PW):
            x, y = K[k]; pk = back((t - 1.3 - 0.08 * i) / 0.3)
            if pk <= 0: continue
            c.circle(x, y, 62 * pk, outline=YEL, w=5, a=1)
            ph = ((t - 1.3) * 1.4 + i * 0.25) % 1
            c.circle(x, y, 64 + 36 * ph, outline=YEL, w=3, a=(1 - ph) * 0.7)
        callout(c, W / 2, 1225, "자국 4개", 62, YEL, ease((t - 1.65) / 0.12), 0.7 + 0.3 * back((t - 1.65) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

# ---------------------------------------------------------------- 2. 4×3×2×1 = 24
PERMS = ["".join(p) for p in itertools.permutations(PW)]
def perm(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 41-B  |  순서는 몇 가지?")
    a0 = ease(t / 0.25)
    for i, k in enumerate(PW):                                   # 자국 난 키 4개
        x = 540 + (i - 1.5) * 130; pk = back((t - 0.05 - 0.06 * i) / 0.3)
        c.rrect((x - 50 * pk, 400 - 50 * pk, x + 50 * pk, 400 + 50 * pk), 18, fill=(24, 30, 44), outline=YEL, w=4, a=a0)
        c.text(x, 400, k, 56 * max(pk, 0.05), YEL, a0)
    nums = ["4", "×", "3", "×", "2", "×", "1"]
    xs = [540 + (i - 3) * 82 for i in range(7)]
    for i, (s_, x) in enumerate(zip(nums, xs)):                  # 식이 한 칸씩 쾅
        tt = t - 0.35 - 0.11 * i
        if tt < 0: continue
        pk = back(tt / 0.25)
        c.text(x, 545, s_, 78 * max(pk, 0.05), LINE if s_ == "×" else CYAN, 1, stroke=4)
    if t > 1.15:
        pk = back((t - 1.15) / 0.3)
        c.text(540, 650, "= 24", 110 * max(pk, 0.05), YEL, 1, stroke=5)
    n = int(24 * eexpo((t - 0.9) / 1.2))                        # 경우의 수 24칸
    gx0, gy0, cw, ch = 150, 760, 196, 66
    for i in range(24):
        col_, row = i % 4, i // 4
        x = gx0 + col_ * cw + cw / 2 - 98 + 98; y = gy0 + row * ch
        if i < n:
            hot = PERMS[i] == "2579"
            fill = mix(CYAN, BG_N, 0.6) if not hot else mix(YEL, BG_N, 0.35)
            c.rrect((x - 86, y - 24, x + 86, y + 24), 24, fill=fill, a=1)
            c.text(x, y, " ".join(PERMS[i]), 34, (255, 255, 255), 1)
        else:
            c.rrect((x - 86, y - 24, x + 86, y + 24), 24, outline=mix(DIM, BG_N, 0.3), w=2, a=a0 * 0.6)
    if t > 2.15:
        callout(c, W / 2, 1210, "딱 24가지!", 64, YEL, ease((t - 2.15) / 0.12), 0.7 + 0.3 * back((t - 2.15) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

# ---------------------------------------------------------------- 3. 허수 입력 → 열림
SEQ = [("6", 0), ("1", 0), ("8", 0), ("2", 1), ("5", 1), ("7", 1), ("9", 1)]
def padlock(c, x, y, s, openk, col, a):
    lift = 34 * openk * s; tilt = 0
    c.rrect((x - 54 * s, y - 10 * s, x + 54 * s, y + 70 * s), 14 * s, fill=col, a=a)
    pts = [(x + 34 * s * math.cos(th), y - 10 * s - lift - 40 * s * math.sin(th)) for th in np.linspace(0, math.pi, 24)]
    pts = [(x + 34 * s, y - 10 * s - lift + (0 if openk < 0.5 else 0))] + pts + [(x - 34 * s, y - 10 * s - lift * (1 - openk) - 4)]
    c.line(pts, col, 14 * s, a)
    c.circle(x, y + 26 * s, 9 * s, fill=(20, 30, 50), a=a)

def fake(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 41-C  |  허수 기능")
    a0 = ease(t / 0.25)
    # 입력창
    c.rrect((110, 400, 830, 520), 30, fill=(8, 22, 46), outline=LINE, w=3, a=a0)
    T0, DT = 0.3, 0.2
    nshow = int(max(0, (t - T0) / DT)) + (1 if t >= T0 else 0)
    for i, (d, real) in enumerate(SEQ[:min(nshow, len(SEQ))]):
        x = 170 + i * 92; pk = back((t - T0 - DT * i) / 0.18)
        col = YEL if real else (150, 160, 180)
        c.text(x, 460, d, 64 * max(pk, 0.05), col, 1, stroke=3)
    if t > T0 + DT * 3:
        la = ease((t - T0 - DT * 3) / 0.2)
        c.line([(130, 548), (400, 548)], (150, 160, 180), 4, la); c.text(265, 585, "아무 숫자", 34, (170, 180, 200), la)
    if t > T0 + DT * 7:
        la = ease((t - T0 - DT * 7) / 0.2)
        c.line([(410, 548), (800, 548)], YEL, 4, la); c.text(605, 585, "진짜 비밀번호", 34, YEL, la)
    # 자물쇠
    ok = ease((t - (T0 + DT * 7 + 0.15)) / 0.3)
    padlock(c, 940, 460, 0.9, ok, mix((200, 206, 220), GREEN, ok), a0)
    if ok > 0:
        ph = ((t - T0 - DT * 7) * 1.2) % 1
        c.circle(940, 470, 70 + 50 * ph, outline=GREEN, w=4, a=(1 - ph) * ok)
    # 키패드 (누를 때마다 번쩍)
    K = key_centers(540, 760, 140, 120)
    panel(c, 540, 680, 1160, 440, a0)
    for i, (d, real) in enumerate(SEQ):
        tt = t - T0 - DT * i
        if 0 <= tt < 0.22:
            x, y = K[d]; k = 1 - tt / 0.22
            c.circle(x, y, 50, fill=mix((40, 50, 70), YEL if real else (200, 210, 230), k), a=1)
    digits(c, K, 50, a0)
    if ok > 0.5:
        callout(c, W / 2, 1225, "그래도 열려요!", 62, GREEN, ease((t - T0 - DT * 7 - 0.3) / 0.12), 0.7 + 0.3 * back((t - T0 - DT * 7 - 0.3) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

# ---------------------------------------------------------------- 4. 열화상: 4곳만 vs 전체로 퍼짐
_CM = None
def thermal(v):
    global _CM
    if _CM is None:
        stops = [(0, (20, 10, 40)), (0.25, (90, 20, 120)), (0.5, (220, 40, 60)), (0.75, (255, 150, 40)), (1, (255, 250, 210))]
        lut = np.zeros((256, 3), np.float32)
        for i in range(256):
            x = i / 255
            for (p0, c0), (p1, c1) in zip(stops[:-1], stops[1:]):
                if p0 <= x <= p1:
                    k = (x - p0) / (p1 - p0); lut[i] = np.array(c0) + (np.array(c1) - np.array(c0)) * k
        _CM = lut
    return _CM[(np.clip(v, 0, 1) * 255).astype(np.int32)]

def heat_layer(cx, y0, w, h, weights, K, a):
    yy, xx = np.mgrid[0:h // 2, 0:w // 2].astype(np.float32) * 2
    v = np.zeros_like(xx)
    for k, wt in weights.items():
        kx, ky = K[k][0] - (cx - w / 2), K[k][1] - y0
        v += wt * np.exp(-(((xx - kx) ** 2 + (yy - ky) ** 2) / (2 * 42 ** 2)))
    v = np.clip(v, 0, 1)
    rgb = thermal(v)
    img = np.zeros((h // 2, w // 2, 4), np.uint8); img[..., :3] = rgb.astype(np.uint8); img[..., 3] = int(255 * a)
    im = Image.fromarray(img, "RGBA").resize((w, h), Image.BILINEAR)
    m = Image.new("L", (w, h), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], 30, fill=int(255 * a))
    im.putalpha(m); return im

def heat(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 41-D  |  열화상으로 본 지문 자국")
    a0 = ease(t / 0.25); w, h, y0 = 400, 560, 520
    sides = [(290, "허수 안 쓰면", HOT), (790, "허수 쓰면", GREEN)]
    spread = ease((t - 0.45) / 1.6)
    rng = np.random.default_rng(41); jitter = {k: rng.uniform(0.55, 0.8) for k in KEYS}
    for j, (cx, lab, lc) in enumerate(sides):
        K = key_centers(cx, y0 + 95, 120, 125)
        if j == 0: wts = {k: (0.95 if k in PW else 0.0) for k in KEYS}
        else: wts = {k: (lerp(0.95, 0.72, spread) if k in PW else jitter[k] * spread) for k in KEYS}
        c.rrect((cx - w / 2 - 8, y0 - 8, cx + w / 2 + 8, y0 + h + 8), 38, outline=(150, 158, 172), w=10, a=a0)
        base.alpha_composite(heat_layer(cx, y0, w, h, wts, K, a0), (int(cx - w / 2), y0))
        digits(c, K, 46, a0, {k: (255, 255, 255) for k in KEYS})
        c.text(cx, y0 - 56, lab, 44, lc, a0, stroke=3)
        if j == 0 and t > 1.2:
            for i, k in enumerate(PW):
                x, y = K[k]; c.circle(x, y, 48, outline=YEL, w=4, a=ease((t - 1.2 - 0.06 * i) / 0.2))
        if j == 1 and t > 2.0:
            for i, k in enumerate(["1", "5", "9", "0"]):
                x, y = K[k]; pk = back((t - 2.0 - 0.08 * i) / 0.3)
                if pk > 0: c.text(x + 40, y - 40, "?", 54 * pk, YEL, 1, stroke=4)
    # 범례
    la = ease((t - 0.3) / 0.3)
    for j in range(30):
        k = j / 29; col = tuple(int(v) for v in thermal(np.array([k]))[0])
        c.rrect((290 + k * 500, 1135, 290 + k * 500 + 18, 1155), 0, fill=col, a=la)
    c.text(270, 1145, "적게", 28, LINE, la, anchor="rm"); c.text(812, 1145, "많이 누름", 28, LINE, la, anchor="lm")
    if t > 2.3:
        callout(c, W / 2, 1230, "어디가 비밀번호?", 58, YEL, ease((t - 2.3) / 0.12), 0.7 + 0.3 * back((t - 2.3) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

# ---------------------------------------------------------------- 5. 설명서 3장
BOOKS = [("앞에 누르기", "아무 숫자 → 비밀번호"), ("중간에 끼우기", "비밀번호 사이에"), ("자릿수 제한", "최대 몇 자리까지")]
def manual(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 41-E  |  제품마다 달라요")
    xs = [215, 540, 865]
    for i, ((h1, h2), x) in enumerate(zip(BOOKS, xs)):
        k = back((t - 0.15 - 0.15 * i) / 0.4); a = ease((t - 0.15 - 0.15 * i) / 0.2)
        if a <= 0: continue
        y = 700 + (1 - k) * 300
        c.rrect((x - 140, y - 230, x + 140, y + 230), 22, fill=(236, 240, 248), a=a)
        c.rrect((x - 140, y - 230, x + 140, y - 150), 22, fill=mix(CYAN, BG_N, 0.25 + 0.15 * i), a=a)
        c.text(x, y - 192, "설명서", 34, (255, 255, 255), a)
        # 미니 키패드
        for r in range(4):
            for q in range(3):
                kx, ky = x - 50 + q * 50, y - 110 + r * 44
                c.rrect((kx - 18, ky - 16, kx + 18, ky + 16), 8, fill=(40, 48, 64), a=a)
        mk = [((1, 1), YEL), ((2, 0), (150, 160, 180))] if i == 0 else ([((0, 1), YEL), ((1, 2), (150, 160, 180))] if i == 1 else [((3, 1), YEL)])
        for (r, q), col in mk:
            kx, ky = x - 50 + q * 50, y - 110 + r * 44
            c.rrect((kx - 18, ky - 16, kx + 18, ky + 16), 8, fill=col, a=a)
        c.text(x, y + 105, h1, 36, (20, 30, 50), a)
        c.text(x, y + 158, h2, 26, (80, 90, 110), a)
    if t > 1.2:                                                   # 돋보기 + 체크
        k = eout((t - 1.2) / 0.5); mx = lerp(130, 540, k); my = 1010
        c.circle(mx, my, 70, outline=LINE, w=10, a=1); c.line([(mx + 50, my + 50), (mx + 110, my + 110)], LINE, 16, 1)
        c.circle(mx, my, 62, fill=(30, 60, 100), a=0.55)
        if t > 1.7:
            pk = back((t - 1.7) / 0.3)
            c.line([(mx - 26 * pk, my), (mx - 6 * pk, my + 22 * pk), (mx + 30 * pk, my - 22 * pk)], GREEN, 12, 1)
            callout(c, W / 2, 1225, "설명서 확인!", 62, GREEN, ease((t - 1.75) / 0.12), 0.7 + 0.3 * back((t - 1.75) / 0.3))
    return intro_fade(c.compose(base, glow=0.75), t).convert("RGB")

SCENES = {"uv": uv, "perm": perm, "fake": fake, "heat": heat, "manual": manual}
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
