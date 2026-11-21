"""42편 달리기(힐락) 설계도 모션그래픽 6장면.
gait: 옆 단면 — 걸을 때 뒤꿈치가 들썩이고 뒤꿈치 쪽이 쓸려 빨갛게 / name: 위에서 본 신발, 맨 위 7번째 구멍 = 힐락 구멍 /
step1: 같은 쪽 맨 위 구멍에 넣어 작은 고리 / step2: 반대쪽 끈을 고리에 엇갈려 넣기 / step3: 아래로 당기면 고리가 조여 붙고 리본 /
locked: 다시 단면 — 뒤꿈치 고정, 쓸림 사라짐
근거: ASICS(힐락: 뒤꿈치 미끄러짐을 막고 마찰을 줄여 물집 예방), Road Runner Sports(맨 위 구멍으로 양쪽 고리 → 반대쪽 고리에 넣고 아래로 당김)
usage: python3 bp42.py <scene> out.mp4 dur | out.jpg t1 t2 ..."""
import math, os, subprocess, sys
import numpy as np
from PIL import Image
from bp30v2 import (W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back,
                    LINE, CYAN, YEL, HOT, ORANGE)
from bp40 import lerp, mix, eexpo, GREEN, DIM, BG_N

SKIN = (236, 196, 160); SOLE = (226, 230, 238); MID = (170, 180, 196)

def partial(pts, k):
    if k <= 0 or len(pts) < 2: return []
    L = [0.0]
    for a, b in zip(pts[:-1], pts[1:]): L.append(L[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    tgt = L[-1] * min(1, k); out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= tgt: out.append(pts[i])
        else:
            f = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1])
            out.append((lerp(pts[i - 1][0], pts[i][0], f), lerp(pts[i - 1][1], pts[i][1], f))); break
    return out

def lace(c, pts, col, a, w=13):
    if len(pts) < 2: return
    c.line(pts, mix(col, (0, 0, 0), 0.55), w + 6, a)
    c.line(pts, col, w, a)
    c.line(pts, mix(col, (255, 255, 255), 0.55), max(2, w * 0.22), a)

def smooth(pts, n=8):
    """캣멀-롬으로 부드러운 곡선."""
    if len(pts) < 3: return pts
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1]); return out

# ---------------------------------------------------------------- 옆 단면 (걸음)
UPPER = [(0, -62), (-14, -120), (-6, -190), (22, -232), (70, -246), (130, -236), (175, -226), (230, -262), (262, -250), (330, -200), (430, -142), (520, -104), (568, -64)]
FOOT = [(26, -66), (6, -110), (6, -160), (26, -205), (44, -280), (52, -400), (150, -400), (156, -300), (176, -240), (250, -205), (330, -178), (430, -142), (500, -112), (540, -84), (520, -70), (300, -66), (100, -66)]
def side_scene(t, locked, label):
    base = BG.copy(); title_c = Canvas(); title(title_c, t, label)
    a0 = ease(t / 0.25)
    ox, oy, S = 175, 1015, 1.3
    cyc = 0.95; ph = (max(0, t - 0.3) % cyc) / cyc; on = 1 if t > 0.3 else 0
    ang = math.radians(14) * math.sin(math.pi * ph) ** 2 * on              # 발끝 축으로 뒤꿈치 들림
    lift = 0 if locked else 42 * math.sin(math.pi * ph) ** 1.5 * on
    tx, ty = 568, 0
    def P(x, y, dy=0):
        x2, y2 = x - tx, y + dy - ty
        ca, sa = math.cos(ang), math.sin(ang)
        return ox + (tx + x2 * ca + y2 * sa) * S, oy + (ty - x2 * sa + y2 * ca) * S
    # 1층: 바닥선 + 발 + 쓸림
    c1 = Canvas()
    c1.line([(60, oy + 4), (1020, oy + 4)], DIM, 3, a0 * 0.7)
    fp = [P(x, y, -lift) for x, y in smooth(FOOT, 6)]
    c1.poly(fp, (226, 184, 150), a0)
    c1.poly([P(x, y, -lift) for x, y in smooth([(40, -120), (36, -180), (60, -260), (70, -380), (120, -380)], 5)] + [P(120, -120, -lift)], (238, 202, 170), a0 * 0.9)
    heat = 0 if locked else ease((t - 0.6) / 2.0)
    hx, hy = P(4, -140, -lift * 0.5)
    if heat > 0:
        for r, al in ((80, 0.2), (52, 0.35), (28, 0.7)):
            c1.circle(hx, hy, r * (0.6 + 0.4 * heat), fill=mix(ORANGE, HOT, r / 80), a=al * heat * (0.8 + 0.2 * math.sin(t * 20)))
    img = c1.compose(base, glow=0.6)
    # 2층: 비치는 신발(반투명 갑피) + 윤곽 + 밑창
    c2 = Canvas()
    up = [P(x, y) for x, y in smooth(UPPER, 6)]
    c2.poly(up + [P(568, -62), P(0, -62)], (70, 120, 190), a0 * 0.42)
    c2.line(up, LINE, 7, a0)
    c2.line([P(x, y) for x, y in smooth([(2, -62), (-12, -120), (-4, -196)], 6)], (150, 170, 200), 18, a0)      # 뒤꿈치 컵
    c2.poly([P(-8, -64), P(568, -64), P(580, -34), P(566, 0), P(6, 0), P(-18, -30)], MID, a0)
    c2.poly([P(-8, -22), P(572, -22), P(566, 0), P(6, 0)], SOLE, a0)
    for i, xx in enumerate((185, 220, 255, 290)):
        c2.circle(*P(xx, -236 + i * 16), 6, fill=(240, 240, 250), a=a0)
    if not locked and lift > 8:                               # 뒤꿈치가 뜬 틈
        p1, p2 = P(40, -66), P(40, -66, -lift)
        for q in (p1, p2): c2.line([(q[0] - 30, q[1]), (q[0] + 30, q[1])], YEL, 4, 1)
        c2.line([p1, p2], YEL, 3, 1)
    if locked:
        k = ease((t - 0.2) / 0.4); pul = 0.6 + 0.4 * math.sin(t * 8)
        c2.line([P(x, y) for x, y in smooth([(22, -240), (80, -250), (140, -240), (185, -232)], 6)], GREEN, 9, k * pul)
        for q in ((140, -252), (185, -244)):
            c2.circle(*P(*q), 13, outline=GREEN, w=5, a=k)
    img = c2.compose(img, glow=0.7)
    # 3층: 글자·화살표
    c3 = title_c
    if not locked and t > 0.5:
        aa = ease((t - 0.5) / 0.2); x0, y0 = P(-70, -170); x0 = max(110, x0); d = 18 * math.sin(t * 6.6)
        c3.arrow(x0 - 30, y0 + 60 + d, x0 - 30, y0 - 80 + d, YEL, 9, 26, aa, both=True)
        c3.text(x0 - 30, y0 - 140, "들썩!", 46, YEL, aa, stroke=3)
    if locked and t > 1.2:
        pk = max(0.05, back((t - 1.2) / 0.3)); gx, gy = P(-60, -300)
        c3.circle(gx, gy, 46 * pk, fill=GREEN, a=1)
        c3.line([(gx - 20, gy), (gx - 4, gy + 16), (gx + 22, gy - 16)], (255, 255, 255), 8, 1)
    lab, col, tt = ("뒤꿈치 착!", GREEN, 1.5) if locked else ("쓸려서 물집!", HOT, 2.0)
    if t > tt:
        callout(c3, W / 2, 1215, lab, 62, col, ease((t - tt) / 0.12), 0.7 + 0.3 * back((t - tt) / 0.3))
    return intro_fade(c3.compose(img, glow=0.8), t).convert("RGB")
def gait(t): return side_scene(t, False, "DWG. 42-A  |  걸을 때 신발 속 단면")
def locked(t): return side_scene(t, True, "DWG. 42-F  |  힐락으로 묶으면")

# ---------------------------------------------------------------- 위에서 본 신발
CX = 540
ROWS = [1000, 930, 860, 790, 720, 650]
def eye(i, side):                       # i: 0~5 일반, 6 = 힐락 구멍
    if i == 6: return (CX + side * 128, 560)
    return (CX + side * (78 + i * 3.4), ROWS[i])
def shoe_top(c, P, a):
    out = []
    for th in np.linspace(0, 2 * math.pi, 120):
        rx = 190 if math.sin(th) > 0 else 170
        x = CX + rx * math.cos(th) * (1 - 0.18 * max(0, -math.sin(th)))
        y = 820 + 400 * math.sin(th)
        out.append(P((x, y)))
    c.poly(out, (22, 44, 82), a)
    c.line(out + [out[0]], LINE, 5, a)
    tongue = [P((CX - 70, 1050)), P((CX - 88, 600)), P((CX - 60, 470)), P((CX + 60, 470)), P((CX + 88, 600)), P((CX + 70, 1050))]
    c.poly(tongue, (34, 62, 104), a)
def eyelets(c, P, a, upto=6, hl7=0.0):
    for i in range(7):
        for s in (-1, 1):
            x, y = P(eye(i, s)); big = i == 6
            col = YEL if (big and hl7 > 0) else (205, 212, 226)
            c.circle(x, y, 15 * (1.15 if big else 1), fill=(10, 18, 34), outline=col, w=5, a=a)
def crisscross(c, P, a, upto=5):
    for i in range(upto):
        for s in (-1, 1):
            p, q = P(eye(i, s)), P(eye(i + 1, -s))
            lace(c, [p, q], YEL if s < 0 else CYAN, a, 11)
def name(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 42-B  |  위에서 본 운동화")
    a0 = ease(t / 0.25); P = lambda p: p
    shoe_top(c, P, a0); crisscross(c, P, a0); eyelets(c, P, a0, hl7=1 if t > 0.9 else 0)
    k = (t - 0.2) / 0.7                                       # 아래부터 구멍 하나씩 반짝
    for i in range(7):
        if 0 < k * 7 - i < 1:
            for s in (-1, 1):
                x, y = eye(i, s); c.circle(x, y, 26, outline=CYAN, w=4, a=1 - (k * 7 - i))
    if t > 0.9:
        pk = back((t - 0.9) / 0.35); pul = 0.6 + 0.4 * math.sin(t * 9)
        for s in (-1, 1):
            x, y = eye(6, s)
            c.circle(x, y, 34 * max(pk, 0.05), outline=YEL, w=6, a=1)
            ph = ((t - 0.9) * 1.3) % 1; c.circle(x, y, 36 + 40 * ph, outline=YEL, w=3, a=(1 - ph) * pul)
        la = ease((t - 1.15) / 0.2)
        c.line([eye(6, 1), (850, 470)], YEL, 3, la)
        c.rrect((760, 420, 1010, 480), 30, fill=(8, 26, 56), outline=YEL, w=3, a=la)
        c.text(885, 449, "7번째 구멍", 32, YEL, la)
    if t > 1.5:
        callout(c, W / 2, 1225, "힐락 구멍!", 64, YEL, ease((t - 1.5) / 0.12), 0.7 + 0.3 * back((t - 1.5) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")

# ---------------------------------------------------------------- 묶는 법 (확대)
Z = 1.85
def PZ(p): return (CX + (p[0] - CX) * Z, 690 + (p[1] - 640) * Z)
def loop_pts(side, r):
    ex, ey = eye(6, side); cx = ex + side * (r + 6); pts = [(ex, ey)]
    for th in np.linspace(0, 2 * math.pi, 28):
        pts.append((cx - side * r * math.cos(th), ey - r * 0.9 * math.sin(th) * side))
    pts.append((ex, ey)); return pts, (cx, ey)
def base_zoom(c, a):
    shoe_top(c, PZ, a); crisscross(c, PZ, a, upto=5); eyelets(c, PZ, a, hl7=1)
def step_badge(c, n, txt, a):
    c.circle(150, 430, 44, fill=YEL, a=a); c.text(150, 428, n, 48, (20, 26, 40), a)
    c.text(215, 430, txt, 40, LINE, a, anchor="lm", stroke=3)
def step1(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 42-C  |  힐락 묶는 법 ①")
    a0 = ease(t / 0.25); base_zoom(c, a0); step_badge(c, "1", "같은 쪽 맨 위 구멍에 → 작은 고리", ease((t - 0.1) / 0.2))
    for s, col, d in ((-1, YEL, 0.0), (1, CYAN, 0.25)):
        k = ease((t - 0.35 - d) / 1.0)
        lp, _ = loop_pts(s, 34)
        path = [eye(5, s)] + lp
        lace(c, [PZ(p) for p in partial(smooth(path, 4), k)], col, 1, 14)
    if t > 1.7:
        for s in (-1, 1):
            _, ctr = loop_pts(s, 34); x, y = PZ(ctr)
            c.circle(x, y, 80, outline=(255, 255, 255), w=3, a=ease((t - 1.7) / 0.2) * (0.6 + 0.4 * math.sin(t * 8)))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")
def step2(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 42-D  |  힐락 묶는 법 ②")
    a0 = ease(t / 0.25); base_zoom(c, a0); step_badge(c, "2", "반대쪽 고리에 엇갈려 넣기", ease((t - 0.1) / 0.2))
    for s, col in ((-1, YEL), (1, CYAN)):
        lp, _ = loop_pts(s, 34); lace(c, [PZ(p) for p in smooth([eye(5, s)] + lp, 4)], col, 1, 14)
    for s, col, d in ((-1, YEL, 0.0), (1, CYAN, 0.3)):
        _, other = loop_pts(-s, 34); ex, ey = eye(6, s)
        path = [(ex, ey), (CX + s * 30, ey + 40), (CX - s * 30, ey + 12), (other[0], other[1]), (other[0] + s * 10, other[1] + 70)]
        k = ease((t - 0.3 - d) / 1.1)
        lace(c, [PZ(p) for p in partial(smooth(path, 8), k)], col, 1, 14)
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")
def step3(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 42-E  |  힐락 묶는 법 ③")
    a0 = ease(t / 0.25); base_zoom(c, a0); step_badge(c, "3", "아래로 당겨서 평소처럼 묶기", ease((t - 0.1) / 0.2))
    pull = ease((t - 0.3) / 0.8); r = lerp(34, 9, pull)
    for s, col in ((-1, YEL), (1, CYAN)):
        lp, _ = loop_pts(s, r); lace(c, [PZ(p) for p in smooth([eye(5, s)] + lp, 4)], col, 1, 14)
    B = (CX, lerp(700, 735, pull))
    for s, col in ((-1, YEL), (1, CYAN)):
        _, other = loop_pts(-s, r); ex, ey = eye(6, s)
        end = (lerp(other[0] + s * 10, B[0] - s * 12, pull), lerp(other[1] + 70, B[1], pull))
        path = [(ex, ey), (CX + s * 30, ey + 40), (CX - s * 30, ey + 12), (other[0], other[1]), end]
        lace(c, [PZ(p) for p in smooth(path, 8)], col, 1, 14)
    if 0.3 < t < 1.2:
        aa = ease((t - 0.3) / 0.15) * (1 - ease((t - 1.0) / 0.2))
        for s in (-1, 1):
            x, y = PZ((CX + s * 150, 600)); c.arrow(x, y, x, y + 160, (255, 255, 255), 8, 22, aa)
    if t > 1.2:                                                # 리본
        bk = max(0.05, back((t - 1.2) / 0.35)); bx, by = PZ((CX, 745))
        for s, col in ((-1, YEL), (1, CYAN)):
            pts = [(bx + s * 110 * bk * math.cos(th) * (1 + 0.2 * math.sin(th)), by + 50 * bk * math.sin(th)) for th in np.linspace(-math.pi / 2, math.pi * 1.5, 30)]
            pts = [(bx + (p[0] - bx) * 0.5 + s * 55 * bk, p[1]) for p in pts]
            lace(c, pts, col, 1, 12)
            lace(c, [(bx, by), (bx + s * 40 * bk, by + 120 * bk)], col, 1, 12)
        c.circle(bx, by, 16, fill=(255, 255, 255), a=1)
    if t > 1.6:
        callout(c, W / 2, 1225, "완성!", 66, GREEN, ease((t - 1.6) / 0.12), 0.7 + 0.3 * back((t - 1.6) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")

SCENES = {"gait": gait, "name": name, "step1": step1, "step2": step2, "step3": step3, "locked": locked}
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
