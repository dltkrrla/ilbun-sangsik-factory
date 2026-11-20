"""31편 3번째 장면: 병 속 압력 5~7기압을 설계도(블루프린트) 모션그래픽으로.
병을 선으로 그리고 → 기포가 차오르며 안쪽 화살표가 커지고 → 압력계 바늘이 5~7 구간까지 올라간다.
usage: python3 blueprint31a.py out.mp4  |  python3 blueprint31a.py prev.jpg t1 t2 ..."""
import math, os, random, subprocess, sys
from PIL import Image, ImageDraw
from blueprint31 import GRID, F, W, H, FPS, LINE, CYAN, YEL, RED, ease, back, label

D = 4.5
CX, TOPY, BODY_T, BODY_B, HW = 360, 330, 520, 1120, 150      # 병 중심 x, 뚜껑 위, 몸통 위·아래, 몸통 반폭

def bottle_pts(bulge):
    hw = HW * (1 + bulge)
    L = [(CX, TOPY), (CX - 52, TOPY), (CX - 52, TOPY + 52), (CX - 34, TOPY + 52), (CX - 34, TOPY + 100)]
    for i in range(1, 13):                                   # 어깨
        a = i / 12; L.append((CX - 34 - (hw - 34) * ease(a), TOPY + 100 + (BODY_T - TOPY - 100) * a))
    for i in range(1, 21):                                   # 몸통(압력에 따라 살짝 불룩)
        a = i / 20; L.append((CX - hw - 60 * bulge * math.sin(math.pi * a), BODY_T + (BODY_B - BODY_T) * a))
    for i in range(1, 25):                                   # 꽃잎 바닥: 옆에서 본 물결(왼쪽 절반)
        a = i / 24; x = CX - hw + hw * a
        y = BODY_B + 40 * math.sin(math.pi * a / 2) ** 0.6 + 34 * abs(math.sin(1.5 * math.pi * a))
        L.append((x, y))
    Rr = [(2 * CX - x, y) for x, y in reversed(L[:-1])]
    return L + Rr

def partial(pts, f):
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; tot = sum(seg)
    if f >= 1: return pts
    out = [pts[0]]; left = tot * f
    for i, s in enumerate(seg):
        if left <= s:
            a = left / s if s else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * a, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * a)); break
        out.append(pts[i + 1]); left -= s
    return out

random.seed(31)
BUB = [(random.uniform(-1, 1), random.uniform(0, 1), random.uniform(5, 14), random.uniform(0.25, 0.6), random.uniform(0, 4)) for _ in range(70)]

GX, GY, GR = 820, 680, 185                                      # 압력계
def gauge_angle(v):                                            # 0~8기압 → 225°~-45°
    return math.radians(225 - 270 * v / 8)

def pressure(t):
    p = 6.0 * ease((t - 0.8) / 1.9)
    if t > 2.7:
        p += 0.35 * math.sin((t - 2.7) * 9) * math.exp(-(t - 2.7) * 1.2)
    return max(0.0, p)

def frame(t):
    im = GRID.copy().convert("RGBA")
    a_grid = ease(t / 0.25)
    if a_grid < 1:
        im = Image.blend(Image.new("RGBA", (W, H), (6, 22, 46, 255)), im, a_grid)
    d = ImageDraw.Draw(im)
    label(d, "DWG. 31-A  |  탄산음료 병 속 압력", 70, 250, 34, CYAN, a=ease((t - 0.1) / 0.3))
    p = pressure(t); bulge = 0.035 * p / 6
    pts = bottle_pts(bulge)
    # 액체 + 기포
    if t > 0.5:
        a = ease((t - 0.5) / 0.4)
        liq = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(liq)
        ld.polygon([(x, max(y, 560)) for x, y in pts], fill=(120, 60, 30, int(70 * a)))
        for bx, by, r, sp, ph in BUB:
            n = min(1.0, 0.25 + p / 6)
            if (bx + 1) / 2 > n: continue
            yy = BODY_B + 20 - ((by + (t * sp) + ph) % 1.0) * (BODY_B + 20 - 580)
            xx = CX + bx * (HW - 24) + 6 * math.sin(t * 3 + ph * 5)
            ld.ellipse((xx - r, yy - r, xx + r, yy + r), outline=LINE + (int(170 * a),), width=2)
        im.alpha_composite(liq); d = ImageDraw.Draw(im)
    # 외곽선
    pp = partial(pts, ease(t / 0.7))
    if len(pp) > 1:
        d.line(pp, fill=LINE + (255,), width=7, joint="curve")
    # 안쪽에서 밖으로 미는 화살표
    if p > 0.2:
        k = p / 6
        for i in range(10):
            ang = 2 * math.pi * i / 10 + 0.3
            cx0, cy0 = CX, 840
            r0, r1 = 40, 40 + 85 * k
            ex, ey = 0.92 * HW / 125, 1.0
            x0, y0 = cx0 + r0 * math.cos(ang) * ex, cy0 + r0 * math.sin(ang) * 2.0
            x1, y1 = cx0 + r1 * math.cos(ang) * ex, cy0 + r1 * math.sin(ang) * 2.0
            d.line((x0, y0, x1, y1), fill=YEL + (230,), width=8)
            hx, hy = math.cos(math.atan2(y1 - y0, x1 - x0)), math.sin(math.atan2(y1 - y0, x1 - x0))
            d.polygon([(x1 + hx * 20, y1 + hy * 20), (x1 - hy * 13, y1 + hx * 13), (x1 + hy * 13, y1 - hx * 13)], fill=YEL + (230,))
    # 압력계
    ga = ease((t - 0.35) / 0.4)
    if ga > 0:
        c = lambda col, al=1.0: col + (int(255 * ga * al),)
        d.ellipse((GX - GR, GY - GR, GX + GR, GY + GR), outline=c(LINE), width=7)
        d.arc((GX - GR + 22, GY - GR + 22, GX + GR - 22, GY + GR - 22), -(225 - 270 * 5 / 8), -(225 - 270 * 7 / 8) + 360 if False else -(225 - 270 * 7 / 8),
              fill=c(RED, 0.45 + 0.55 * ease((t - 2.5) / 0.3)), width=26)
        for v in range(0, 9):
            an = gauge_angle(v)
            x0, y0 = GX + (GR - 18) * math.cos(an), GY - (GR - 18) * math.sin(an)
            x1, y1 = GX + (GR - 44) * math.cos(an), GY - (GR - 44) * math.sin(an)
            d.line((x0, y0, x1, y1), fill=c(LINE), width=5)
            tx, ty = GX + (GR - 78) * math.cos(an), GY - (GR - 78) * math.sin(an)
            d.text((tx, ty), str(v), font=F(30), fill=c(LINE), anchor="mm")
        an = gauge_angle(min(8, p))
        d.line((GX, GY, GX + (GR - 50) * math.cos(an), GY - (GR - 50) * math.sin(an)), fill=c(YEL), width=9)
        d.ellipse((GX - 16, GY - 16, GX + 16, GY + 16), fill=c(YEL))
        label(d, "기압", GX, GY + 70, 34, CYAN, anchor="mm", a=ga)
        label(d, "병 속 압력", GX, GY - GR - 50, 44, LINE, anchor="mm", a=ga)
        d.line((CX + HW + 20, 840, GX - GR - 10, GY + 40), fill=CYAN + (int(160 * ga),), width=3)
    # 결과 숫자
    if t >= 2.55:
        k = back((t - 2.55) / 0.3)
        label(d, "5~7기압", GX, GY + GR + 95, int(104 * (0.6 + 0.4 * k)), YEL, anchor="mm", a=ease((t - 2.55) / 0.12))
    return im.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]
    if len(sys.argv) > 2:
        ims = [frame(float(v)).resize((270, 480), Image.LANCZOS) for v in sys.argv[2:]]
        s = Image.new("RGB", (270 * len(ims), 480)); [s.paste(m, (i * 270, 0)) for i, m in enumerate(ims)]
        s.save(out, quality=85); raise SystemExit
    tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(D * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, out); print("ok", out)
