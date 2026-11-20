"""30편 설계도 모션그래픽 v2 — 더 정교하게.
- 2배 크기로 그리고 줄여서 선이 매끈함(supersampling) + 네온 글로우
- 전자레인지는 실제 구조(문 그물망, 마그네트론, 도파관, 회전 접시)로 단면을 그림
- 센 곳/약한 곳은 실제 정상파 세기(sin²·sin²) 히트맵, 6cm = 반 파장
- 회전 접시 위 음식은 센 곳을 지날 때마다 실제로 데워진 만큼 색이 변함
usage: python3 bp30v2.py <wave|spots|turn|center> out.mp4 dur  |  ... prev.jpg t1 t2 ..."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, S = 1080, 1920, 30, 2                     # S: supersampling 배율
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
_fc = {}
def F(sz):
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, int(sz), index=1)
    return _fc[sz]

NAVY = (10, 34, 70); LINE = (226, 244, 255); CYAN = (110, 210, 255); YEL = (255, 212, 70)
HOT = (255, 92, 60); COLD = (70, 150, 255); ORANGE = (255, 150, 60)

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def eout(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def back(x): x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- 배경: 남색 그라데이션 + 모눈 + 비네트 ----------
def make_bg():
    y = np.linspace(0, 1, H)[:, None]; x = np.linspace(0, 1, W)[None, :]
    r = np.sqrt((x - 0.5) ** 2 + ((y - 0.45) * 1.2) ** 2)
    base = np.clip(1.0 - r * 0.9, 0.35, 1.0)
    img = np.zeros((H, W, 3), np.float32)
    for i, c in enumerate((18, 52, 98)):
        img[..., i] = c * base
    g = np.zeros((H, W), np.float32)
    g[:, ::40] = 0.10; g[::40, :] = 0.10; g[:, ::200] = 0.22; g[::200, :] = 0.22
    for i, c in enumerate((120, 190, 255)):
        img[..., i] += g * c * base
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
BG = make_bg()

class Canvas:
    """2배 크기 벡터 레이어 + 글로우."""
    def __init__(self):
        self.v = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.v)
    def line(self, pts, col, w, a=1.0):
        if len(pts) > 1 and a > 0:
            self.d.line([(x * S, y * S) for x, y in pts], fill=col + (int(255 * a),), width=int(w * S), joint="curve")
    def circle(self, x, y, r, fill=None, outline=None, w=3, a=1.0):
        if a <= 0: return
        self.d.ellipse((x * S - r * S, y * S - r * S, x * S + r * S, y * S + r * S),
                       fill=fill + (int(255 * a),) if fill else None, outline=outline + (int(255 * a),) if outline else None, width=int(w * S))
    def rrect(self, box, r, fill=None, outline=None, w=3, a=1.0):
        if a <= 0: return
        self.d.rounded_rectangle([v * S for v in box], r * S, fill=fill + (int(255 * a),) if fill else None,
                                 outline=outline + (int(255 * a),) if outline else None, width=int(w * S))
    def poly(self, pts, fill, a=1.0):
        if a > 0: self.d.polygon([(x * S, y * S) for x, y in pts], fill=fill + (int(255 * a),))
    def text(self, x, y, s, size, col, a=1.0, anchor="mm", stroke=0):
        if a <= 0: return
        self.d.text((x * S, y * S), s, font=F(size * S), fill=col + (int(255 * a),), anchor=anchor,
                    stroke_width=int(stroke * S), stroke_fill=(6, 20, 44, int(255 * a)))
    def arrow(self, x0, y0, x1, y1, col, w=5, head=18, a=1.0, both=False):
        self.line([(x0, y0), (x1, y1)], col, w, a)
        for (ax, ay, bx, by) in ([(x0, y0, x1, y1)] + ([(x1, y1, x0, y0)] if both else [])):
            ang = math.atan2(by - ay, bx - ax)
            p = [(bx, by), (bx - head * math.cos(ang - 0.45), by - head * math.sin(ang - 0.45)),
                 (bx - head * math.cos(ang + 0.45), by - head * math.sin(ang + 0.45))]
            self.poly(p, col, a)
    def compose(self, base, glow=0.9):
        v = self.v.resize((W, H), Image.LANCZOS)
        if glow > 0:
            for rad, gm in ((22, 0.55), (7, 0.9)):
                g = v.filter(ImageFilter.GaussianBlur(rad))
                ga = np.array(g).astype(np.float32); ga[..., 3] = np.clip(ga[..., 3] * glow * gm * 1.6, 0, 255)
                base.alpha_composite(Image.fromarray(ga.astype(np.uint8)))
        base.alpha_composite(v)
        return base

def callout(c, x, y, s, size, col, a, sc=1.0):
    """둥근 상자 안의 강조 글자."""
    if a <= 0: return
    f = F(size * sc); w = f.getlength(s); h = size * sc * 1.55
    c.rrect((x - w / 2 - 30 * sc, y - h / 2, x + w / 2 + 30 * sc, y + h / 2), h / 2, fill=(8, 26, 56), outline=col, w=4, a=a * 0.95)
    c.text(x, y - 3 * sc, s, size * sc, col, a)

def title(c, t, s):
    a = ease((t - 0.05) / 0.3)
    c.rrect((60, 222, 60 + F(30).getlength(s) + 44, 276), 12, fill=(8, 26, 56), outline=CYAN, w=2, a=a * 0.9)
    c.text(82, 249, s, 30, CYAN, a, anchor="lm")

def intro_fade(base, t):
    if t < 0.25:
        k = ease(t / 0.25); dark = Image.new("RGBA", (W, H), (6, 18, 40, int(255 * (1 - k)))); base.alpha_composite(dark)
    return base

# =====================================================================
# A. 전자레인지 단면 + 멈춰 선 파도
CX0, CX1, CY0, CY1 = 150, 870, 470, 1010            # 조리실(안쪽)
def microwave(c, t):
    k = eout(t / 0.7)
    # 바깥 케이스
    c.rrect((96, 410, 990, 1100), 34, outline=LINE, w=6, a=k)
    # 문(왼쪽) 그물망
    c.rrect((112, 432, 148, 1078), 10, outline=CYAN, w=3, a=k * 0.8)
    for yy in range(450, 1066, 22):
        for xx in (122, 138):
            c.circle(xx, yy, 3, fill=CYAN, a=k * 0.45)
    # 조리실
    c.rrect((CX0, CY0, CX1, CY1), 12, outline=LINE, w=5, a=k)
    # 회전 접시(옆에서 본 모습)
    c.line([(CX0 + 90, CY1 - 34), (CX1 - 90, CY1 - 34)], CYAN, 6, a=k)
    c.line([(CX0 + 330, CY1 - 34), (CX0 + 330, CY1 - 6)], CYAN, 4, a=k)
    # 마그네트론 + 도파관(오른쪽 위)
    ka = eout((t - 0.35) / 0.5)
    c.rrect((892, 470, 972, 640), 14, fill=(30, 40, 70), outline=YEL, w=4, a=ka)
    for i in range(5): c.line([(900, 492 + i * 26), (964, 492 + i * 26)], YEL, 2, a=ka * 0.6)
    c.rrect((CX1 - 4, 600, 892, 660), 6, outline=YEL, w=4, a=ka)
    c.text(930, 384, "마그네트론", 28, YEL, ka)

def wave(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 30-A  |  전자레인지 단면")
    c.rrect((CX0 + 4, CY0 + 4, CX1 - 4, CY1 - 4), 10, fill=(30, 70, 130), a=0.35 * eout(t / 0.7))
    microwave(c, t)
    cy, A, lam = 740, 150, 240.0; k = 2 * math.pi / lam
    trav = eout((t - 0.65) / 0.8); stand = ease((t - 1.45) / 0.45)
    front = CX1 - (CX1 - CX0) * trav
    xs = np.arange(CX0 + 10, CX1 - 10, 3.0)
    inc = np.sin(k * (CX1 - xs) - t * 10)                 # 들어오는 파도
    ref = np.sin(k * (xs - CX0) - t * 10 + math.pi)       # 벽에 부딪혀 돌아오는 파도
    st = np.sin(k * (xs - CX0)) * math.cos(t * 7.5)
    if trav > 0:
        y_in = cy - A * ((1 - stand) * inc + stand * st)
        m = xs >= front
        pts = list(zip(xs[m], y_in[m]))
        c.line(pts, HOT, 7)
        if 0.2 < stand < 1:                               # 돌아오는 파도를 옅게 보여 주며 겹침
            pts2 = list(zip(xs, cy - A * 0.9 * ref)); c.line(pts2, CYAN, 3, a=(1 - stand) * 0.7)
        if trav < 1:                                      # 에너지 입자
            for i in range(10):
                px = front + ((t * 260 + i * 70) % max(1, CX1 - front))
                c.circle(px, cy + 70 * math.sin(i * 1.7 + t * 5), 4, fill=YEL, a=0.8)
    if stand > 0.3:                                       # 정상파 포락선(점선): 출렁이는 최대 폭
        ae = ease((stand - 0.3) / 0.7) * 0.7
        env = np.abs(np.sin(k * (xs - CX0))) * A
        for sgn in (1, -1):
            c.line(list(zip(xs, cy - sgn * env)), CYAN, 2.5, ae * 0.6)
    if stand > 0.4:
        a = ease((stand - 0.4) / 0.6); n = 0
        while CX0 + n * lam / 2 <= CX1:
            x = CX0 + n * lam / 2
            if CX0 + 4 < x < CX1 - 4:
                c.circle(x, cy, 12, fill=COLD, a=a)       # 마디(안 움직이는 점)
                c.circle(x + lam / 4, cy, 9 + 4 * abs(math.cos(t * 7.5)), outline=HOT, w=3, a=a * 0.8) if x + lam / 4 < CX1 else None
            n += 1
    if t > 1.85:
        kk = back((t - 1.85) / 0.35); a = ease((t - 1.85) / 0.12)
        callout(c, W / 2, 1200, "멈춰 선 파도", 64, YEL, a, 0.7 + 0.3 * kk)
        c.text(W / 2, 1268, "제자리에서 출렁이며 센 곳·약한 곳이 생겨요", 30, LINE, ease((t - 2.2) / 0.3))
    if t > 2.1:
        a = ease((t - 2.1) / 0.3)
        c.circle(200, 1325, 11, fill=COLD, a=a); c.text(222, 1325, "안 움직이는 점", 28, LINE, a, anchor="lm")
        c.circle(560, 1325, 11, outline=HOT, w=4, a=a); c.text(582, 1325, "가장 센 점", 28, LINE, a, anchor="lm")
    return intro_fade(c.compose(base), t).convert("RGB")

# =====================================================================
# B. 바닥 히트맵 (정상파 세기), 6cm = 반 파장
GX0, GX1, GY0, GY1 = 120, 960, 420, 1150
SP = 150                                             # 6cm = 150px (반 파장)
def heat_rgba():
    xs = np.arange(GX0, GX1); ys = np.arange(GY0, GY1)
    X, Y = np.meshgrid(xs, ys)
    kx = math.pi / SP
    I = (np.sin(kx * (X - GX0 + SP * 0.5)) ** 2) * (np.sin(kx * (Y - GY0 + SP * 0.43)) ** 2)
    I = I ** 0.42
    stops = [(0.0, (40, 90, 220)), (0.35, (90, 70, 200)), (0.6, (220, 70, 90)), (0.85, (255, 140, 50)), (1.0, (255, 230, 120))]
    rgb = np.zeros(I.shape + (3,), np.float32)
    for (a0, c0), (a1, c1) in zip(stops, stops[1:]):
        m = (I >= a0) & (I <= a1); f = ((I - a0) / (a1 - a0))[m][:, None]
        rgb[m] = np.array(c0) * (1 - f) + np.array(c1) * f
    alpha = np.full(I.shape, 235, np.float32)
    out = np.dstack([rgb, alpha]).astype(np.uint8)
    return Image.fromarray(out, "RGBA"), I
HEAT, HEATI = heat_rgba()
def hot_centers():
    pts = []
    for r in range(10):
        for q in range(10):
            x = GX0 + SP * 0.5 + q * SP - SP * 0.5 + SP * 0.5
            y = GY0 + SP * 0.57 + r * SP - SP * 0.5 + SP * 0.5
            xx = GX0 + (q + 0.5) * SP - SP * 0.5 * 0 ; yy = GY0 + (r + 0.5) * SP
            pts.append((xx, yy))
    return pts

def spots(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 30-B  |  조리실 바닥 (위에서 본 모습)")
    # 히트맵: 가운데에서 퍼지듯 드러남
    k = eout((t - 0.3) / 1.0)
    if k > 0:
        hm = HEAT.copy()
        w, h = hm.size; yy, xx = np.mgrid[0:h, 0:w]
        rr = np.sqrt((xx - w / 2) ** 2 + (yy - h / 2) ** 2) / math.hypot(w / 2, h / 2)
        mask = np.clip((k * 1.15 - rr) / 0.12, 0, 1)
        a = np.array(hm)[..., 3].astype(np.float32) * mask
        arr = np.array(hm); arr[..., 3] = a.astype(np.uint8)
        rgbf = arr[..., :3].astype(np.float32) * (0.93 + 0.07 * math.sin(t * 5))
        arr[..., :3] = np.clip(rgbf, 0, 255).astype(np.uint8)
        hm = Image.fromarray(arr)
        base.alpha_composite(hm, (GX0, GY0))
    c.rrect((GX0 - 4, GY0 - 4, GX1 + 4, GY1 + 4), 10, outline=LINE, w=5, a=eout(t / 0.5))
    # 색 막대(범례)
    if t > 0.6:
        a = ease((t - 0.6) / 0.3)
        for i in range(300):
            f = i / 299; I = f
            stops = [(0.0, (40, 90, 220)), (0.35, (90, 70, 200)), (0.6, (220, 70, 90)), (0.85, (255, 140, 50)), (1.0, (255, 230, 120))]
            for (a0, c0), (a1, c1) in zip(stops, stops[1:]):
                if a0 <= I <= a1:
                    g = (I - a0) / (a1 - a0); col = tuple(int(c0[j] * (1 - g) + c1[j] * g) for j in range(3))
            c.line([(390 + i, 330), (390 + i, 356)], col, 1.2, a)
        c.text(372, 343, "약", 30, COLD, a, anchor="rm"); c.text(708, 343, "센 곳", 30, ORANGE, a, anchor="lm")
    # 아지랑이: 센 곳 위로 열기 입자
    if k > 0.6:
        for m in range(5):
            for n in range(6):
                hx, hy = GX0 + n * SP, GY0 + 0.07 * SP + m * SP
                if not (GX0 + 20 < hx < GX1 - 20 and GY0 + 20 < hy < GY1 - 20): continue
                for q in range(2):
                    ph = (t * 0.9 + q * 0.5 + (m * 7 + n * 3) * 0.13) % 1.0
                    c.circle(hx + 10 * math.sin(ph * 6 + n), hy - 18 - ph * 70, 5 * (1 - ph) + 1, fill=(255, 220, 150), a=(1 - ph) * 0.7 * (k - 0.6) / 0.4)
    # 6cm 치수선: 아랫줄의 이웃한 센 곳 두 개 사이 (= 반 파장)
    if t > 1.7:
        a = ease((t - 1.7) / 0.25); g = eout((t - 1.7) / 0.5)
        yloc = GY0 + 0.07 * SP + 4 * SP; xa, xb = GX0 + 2 * SP, GX0 + 3 * SP
        for xx in (xa, xb):
            c.line([(xx, yloc + 30), (xx, GY1 + 78)], YEL, 3, a * 0.8)
            c.circle(xx, yloc, 34, outline=YEL, w=5, a=a)
        y = GY1 + 58; mid = (xa + xb) / 2
        c.arrow(mid, y, mid + (xb - mid) * g, y, YEL, 5, 18, a)
        c.arrow(mid, y, mid - (mid - xa) * g, y, YEL, 5, 18, a)
        if t > 2.0:
            callout(c, mid, y + 80, "6cm", 60, YEL, ease((t - 2.0) / 0.12), 0.7 + 0.3 * back((t - 2.0) / 0.3))
    return intro_fade(c.compose(base, glow=0.7), t).convert("RGB")

# =====================================================================
# C, D. 위에서 본 회전 접시
PC, PR = (540, 780), 340
def plate(c, ang, a=1.0):
    cx, cy = PC
    c.circle(cx, cy, PR + 14, fill=(160, 210, 255), a=a * 0.08)
    c.circle(cx, cy, PR, outline=LINE, w=6, a=a)
    c.circle(cx, cy, PR - 26, outline=CYAN, w=2, a=a * 0.6)
    # 유리 반사광
    c.d.arc([(cx - PR + 40) * S, (cy - PR + 40) * S, (cx + PR - 40) * S, (cy + PR - 40) * S],
            200 + math.degrees(ang) * 0, 250, fill=(255, 255, 255, int(120 * a)), width=8 * S)
    for k3 in range(3):
        th = ang + k3 * 2 * math.pi / 3
        c.line([(cx + 30 * math.cos(th), cy + 30 * math.sin(th)), (cx + (PR - 40) * math.cos(th), cy + (PR - 40) * math.sin(th))], CYAN, 2, a * 0.5)

def floor_heat(base, a):
    if a <= 0: return
    hm = HEAT.copy(); arr = np.array(hm); arr[..., 3] = (arr[..., 3] * 0.55 * a).astype(np.uint8)
    hm = Image.fromarray(arr).crop((0, 0, 840, 730))
    base.alpha_composite(hm, (PC[0] - 420, PC[1] - 365))

def temp_col(v):
    v = max(0.0, min(1.0, v))
    stops = [(0.0, (70, 150, 255)), (0.5, (255, 200, 80)), (1.0, (255, 90, 60))]
    for (a0, c0), (a1, c1) in zip(stops, stops[1:]):
        if a0 <= v <= a1:
            g = (v - a0) / (a1 - a0); return tuple(int(c0[j] * (1 - g) + c1[j] * g) for j in range(3))

def heat_at(x, y):
    xi, yi = int(x - (PC[0] - 420)), int(y - (PC[1] - 365))
    if 0 <= yi < HEATI.shape[0] and 0 <= xi < HEATI.shape[1]: return float(HEATI[yi, xi])
    return 0.0

def angle_at(t):
    return 0.0 if t < 0.35 else 1.7 * ((t - 0.35) - 0.25 * (1 - math.exp(-(t - 0.35) * 4)))

def turn(t):
    base = BG.copy(); floor_heat(base, ease(t / 0.4)); c = Canvas(); title(c, t, "DWG. 30-C  |  회전 접시 (위에서 본 모습)")
    c.rrect((PC[0] - 422, PC[1] - 367, PC[0] + 422, PC[1] + 367), 10, outline=LINE, w=4, a=ease(t / 0.4) * 0.8)
    a = ease(t / 0.35); cx, cy = PC; ang = angle_at(t)
    plate(c, ang, a)
    for k6 in range(6):                               # 음식 6조각: 지나온 센 곳만큼 데워짐
        acc = 0.0; steps = 40
        for i in range(steps):
            tt = t * i / steps; th = angle_at(tt) + k6 * math.pi / 3
            acc += heat_at(cx + 215 * math.cos(th), cy + 215 * math.sin(th)) * (t / steps)
        th = ang + k6 * math.pi / 3; x, y = cx + 215 * math.cos(th), cy + 215 * math.sin(th)
        col = temp_col(acc / 1.6)
        c.rrect((x - 36, y - 30, x + 36, y + 30), 22, fill=col, outline=(255, 255, 255), w=3, a=a)
        if heat_at(x, y) > 0.7: c.circle(x, y, 50, outline=ORANGE, w=4, a=a * (heat_at(x, y) - 0.7) / 0.3)
    if t > 0.5:
        aa = ease((t - 0.5) / 0.3); r = PR + 55
        pts = [(cx + r * math.cos(math.radians(d)), cy + r * math.sin(math.radians(d))) for d in range(-70, 25, 3)]
        c.line(pts, YEL, 8, aa); e = math.radians(25)
        c.arrow(pts[-2][0], pts[-2][1], cx + r * math.cos(e), cy + r * math.sin(e), YEL, 8, 30, aa)
    if t > 1.5:
        callout(c, W / 2, 1230, "센 곳을 골고루 지나가요", 50, LINE, ease((t - 1.5) / 0.15), 0.7 + 0.3 * back((t - 1.5) / 0.3))
    return intro_fade(c.compose(base, glow=0.6), t).convert("RGB")

def center(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 30-D  |  접시가 돌 때 움직이는 길")
    a = ease(t / 0.2); cx, cy = PC; ang = 3.4 * t
    plate(c, ang, a)
    for rr, w in ((300, 7), (215, 6), (125, 5)):      # 혜성 꼬리처럼 자취
        for j in range(26):
            th = ang - j * 0.07; al = (1 - j / 26) * a
            c.circle(cx + rr * math.cos(th), cy + rr * math.sin(th), w * (1 - j / 40), fill=YEL, a=al * 0.8)
        c.circle(cx + rr * math.cos(ang), cy + rr * math.sin(ang), 17, fill=YEL, a=a)
    pr = 1 + 0.12 * math.sin(t * 9)
    c.circle(cx, cy, 20 * pr, fill=COLD, a=a)
    for i in range(2):                                # 가운데 파동 링
        ph = ((t * 1.6 + i * 0.5) % 1.0)
        c.circle(cx, cy, 30 + 70 * ph, outline=COLD, w=4, a=a * (1 - ph))
    if t > 0.45:
        callout(c, W / 2, 1230, "가운데만 제자리", 58, COLD, ease((t - 0.45) / 0.12), 0.7 + 0.3 * back((t - 0.45) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

SCENES = {"wave": wave, "spots": spots, "turn": turn, "center": center}
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
