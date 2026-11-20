"""30편(전자레인지) 설계도 모션그래픽 4장면.
wave: 전자레인지 단면, 들어오던 파도가 멈춰 선 파도가 됨
spots: 바닥에 센 곳/약한 곳이 번갈아, 6cm 치수선
turn: 위에서 본 회전 접시, 음식이 센 곳을 지나감
center: 접시가 돌 때 바깥 점은 원을 그리고 가운데만 제자리
usage: python3 blueprint30.py <scene> out.mp4 [dur]  |  python3 blueprint30.py <scene> prev.jpg t1 t2 ..."""
import math, os, subprocess, sys
from PIL import Image, ImageDraw
from blueprint31 import GRID, F, W, H, FPS, LINE, CYAN, YEL, RED, ease, back, label

BLUE = (90, 170, 255)
HOT = (255, 96, 70)

def base(t, title):
    im = GRID.copy().convert("RGBA")
    a = ease(t / 0.25)
    if a < 1:
        im = Image.blend(Image.new("RGBA", (W, H), (6, 22, 46, 255)), im, a)
    d = ImageDraw.Draw(im)
    label(d, title, 70, 250, 34, CYAN, a=ease((t - 0.1) / 0.3))
    return im, d

def rect_draw(d, box, f, col=LINE, w=7):
    x0, y0, x1, y1 = box
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(4)]; left = sum(seg) * f; out = [pts[0]]
    for i, s in enumerate(seg):
        if left <= s:
            a = left / s; out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * a, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * a)); break
        out.append(pts[i + 1]); left -= s
    if len(out) > 1:
        d.line(out, fill=col + (255,), width=w, joint="curve")

# ---------- wave ----------
def wave(t):
    im, d = base(t, "DWG. 30-A  |  전자레인지 단면")
    X0, X1, Y0, Y1 = 130, 950, 420, 1060
    rect_draw(d, (X0, Y0, X1, Y1), ease(t / 0.6))
    if t > 0.5:
        a = ease((t - 0.5) / 0.3)
        d.rectangle((X1 - 10, 600, X1 + 50, 880), outline=YEL + (int(255 * a),), width=5)       # 전자파가 나오는 곳
        label(d, "전자파", X1 + 20, 560, 34, YEL, anchor="mm", a=a)
    cy, A, lam = (Y0 + Y1) / 2, 170, 240.0          # 화면에서 파장 240px
    k = 2 * math.pi / lam
    trav = ease((t - 0.6) / 0.9)                    # 1) 오른쪽에서 들어옴
    stand = ease((t - 1.5) / 0.4)                   # 2) 멈춰 선 파도로
    front = X1 - (X1 - X0) * trav
    pts = []
    for x in range(int(X0) + 8, int(X1) - 8, 4):
        if x < front: continue
        travel = math.sin(k * (X1 - x) - t * 9)
        standing = math.sin(k * (x - X0)) * math.cos(t * 7)
        y = cy - A * ((1 - stand) * travel + stand * standing)
        pts.append((x, y))
    if len(pts) > 1:
        d.line(pts, fill=HOT + (255,), width=8, joint="curve")
    if stand > 0.5:                                 # 마디(안 움직이는 점)
        n = 0
        while X0 + n * lam / 2 <= X1:
            x = X0 + n * lam / 2
            if X0 + 5 < x < X1 - 5:
                d.ellipse((x - 11, cy - 11, x + 11, cy + 11), fill=BLUE + (int(255 * min(1, (stand - 0.5) * 2)),))
            n += 1
    if t > 1.9:
        kk = back((t - 1.9) / 0.3)
        label(d, "멈춰 선 파도", W / 2, 1180, int(76 * (0.6 + 0.4 * kk)), YEL, anchor="mm", a=ease((t - 1.9) / 0.12))
    return im.convert("RGB")

# ---------- spots ----------
SP = 150                                            # 화면에서 6cm = 150px
def spots(t):
    im, d = base(t, "DWG. 30-B  |  전자레인지 바닥 (위에서 본 모습)")
    X0, X1, Y0, Y1 = 120, 960, 400, 1150
    rect_draw(d, (X0, Y0, X1, Y1), ease(t / 0.5))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    cols = int((X1 - X0) // SP); rows = int((Y1 - Y0) // SP)
    ox = X0 + ((X1 - X0) - cols * SP) / 2 + SP / 2; oy = Y0 + ((Y1 - Y0) - rows * SP) / 2 + SP / 2
    idx = 0
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c * SP, oy + r * SP
            hot = (r + c) % 2 == 0
            ap = ease((t - 0.5 - idx * 0.03) / 0.25); idx += 1
            if ap <= 0: continue
            rad = 52 * ap * (1 + (0.08 * math.sin(t * 8 + r + c) if hot else 0))
            col = HOT if hot else BLUE
            ld.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col + (int(150 * ap),), outline=col + (255,), width=4)
    im.alpha_composite(lay); d = ImageDraw.Draw(im)
    if t > 1.8:                                     # 6cm 치수선: 같은 줄의 센 곳 두 개 사이 (가운데 줄)
        a = ease((t - 1.8) / 0.3); r = rows - 1         # 맨 아랫줄 센 곳 두 개 사이 = 6cm, 상자 아래에 치수선
        c0 = 0 if (r % 2 == 0) else 1
        xa, xb = ox + c0 * SP, ox + (c0 + 2) * SP; y = Y1 + 50
        for xx in (xa, xb):
            d.line((xx, oy + r * SP + 56, xx, y + 22), fill=YEL + (int(160 * a),), width=3)
        d.line((xa, y, xa + (xb - xa) * a, y), fill=YEL + (255,), width=6)
        for xx in (xa, xa + (xb - xa) * a):
            d.line((xx, y - 22, xx, y + 22), fill=YEL + (255,), width=6)
        if a > 0.8:
            label(d, "6cm", (xa + xb) / 2, y + 62, int(72 * (0.6 + 0.4 * back((t - 2.1) / 0.3))), YEL, anchor="mm", a=ease((t - 2.05) / 0.12))
    if t > 0.9:
        a = ease((t - 0.9) / 0.3)
        d.ellipse((150, 320, 190, 360), fill=HOT + (int(255 * a),)); label(d, "센 곳 (뜨거움)", 205, 340, 40, LINE, a=a)
        d.ellipse((560, 320, 600, 360), fill=BLUE + (int(255 * a),)); label(d, "약한 곳 (차가움)", 615, 340, 40, LINE, a=a)
    return im.convert("RGB")

# ---------- turn / center : 위에서 본 회전 접시 ----------
PC, PR = (540, 780), 360
def plate(d, ang, a=1.0):
    cx, cy = PC
    d.ellipse((cx - PR, cy - PR, cx + PR, cy + PR), outline=LINE + (int(255 * a),), width=7)
    d.ellipse((cx - PR + 26, cy - PR + 26, cx + PR - 26, cy + PR - 26), outline=LINE + (int(90 * a),), width=3)
    for k in range(3):                              # 회전이 보이게 바퀴살 3개
        th = ang + k * 2 * math.pi / 3
        d.line((cx + 40 * math.cos(th), cy + 40 * math.sin(th), cx + (PR - 30) * math.cos(th), cy + (PR - 30) * math.sin(th)),
               fill=CYAN + (int(110 * a),), width=3)

HOTS = [(-150, -150), (150, -150), (0, 0), (-150, 150), (150, 150), (0, -300), (0, 300), (-300, 0), (300, 0)]
def turn(t):
    im, d = base(t, "DWG. 30-C  |  회전 접시 (위에서 본 모습)")
    a = ease(t / 0.4); cx, cy = PC
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for hx, hy in HOTS:                             # 고정된 센 곳(빨강)
        if (hx, hy) == (0, 0): continue
        ld.ellipse((cx + hx - 48, cy + hy - 48, cx + hx + 48, cy + hy + 48), fill=HOT + (int(90 * a),))
    im.alpha_composite(lay); d = ImageDraw.Draw(im)
    ang = 1.6 * ease((t - 0.4) / 0.6) * (t - 0.4) if t > 0.4 else 0.0
    plate(d, ang, a)
    for k in range(6):                              # 접시 위 음식 6조각
        th = ang + k * math.pi / 3; rr = 220
        x, y = cx + rr * math.cos(th), cy + rr * math.sin(th)
        near = min(math.dist((x, y), (cx + hx, cy + hy)) for hx, hy in HOTS if (hx, hy) != (0, 0))
        glow = max(0.0, 1 - near / 80)
        col = tuple(int(YEL[i] * (1 - glow) + HOT[i] * glow) for i in range(3))
        s = 34 + 10 * glow
        d.rounded_rectangle((x - s, y - s, x + s, y + s), 10, fill=col + (int(255 * a),))
    if t > 0.6:                                     # 회전 화살표
        aa = ease((t - 0.6) / 0.3)
        d.arc((cx - PR - 40, cy - PR - 40, cx + PR + 40, cy + PR + 40), -60, 20, fill=YEL + (int(255 * aa),), width=9)
        e = math.radians(20); ex, ey = cx + (PR + 40) * math.cos(e), cy + (PR + 40) * math.sin(e)
        d.polygon([(ex - 4, ey + 30), (ex - 26, ey - 8), (ex + 22, ey - 10)], fill=YEL + (int(255 * aa),))
    if t > 1.6:
        label(d, "센 곳을 골고루 지나가요", W / 2, 1230, int(56 * (0.6 + 0.4 * back((t - 1.6) / 0.3))), LINE, anchor="mm", a=ease((t - 1.6) / 0.15))
    return im.convert("RGB")

def center(t):
    im, d = base(t, "DWG. 30-D  |  접시가 돌 때 움직이는 길")
    cx, cy = PC; a = ease(t / 0.3)
    ang = 2.2 * t
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for rr in (110, 220, 310):                      # 바깥 점들의 자취(원)
        sweep = min(359.0, math.degrees(ang))
        ld.arc((cx - rr, cy - rr, cx + rr, cy + rr), 0, sweep, fill=YEL + (150,), width=5)
    im.alpha_composite(lay); d = ImageDraw.Draw(im)
    plate(d, ang, a)
    for rr in (110, 220, 310):
        x, y = cx + rr * math.cos(ang), cy + rr * math.sin(ang)
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=YEL + (int(255 * a),))
    pulse = 1 + 0.15 * math.sin(t * 8)
    r0 = 22 * pulse
    d.ellipse((cx - r0, cy - r0, cx + r0, cy + r0), fill=BLUE + (int(255 * a),))
    if t > 0.9:
        aa = ease((t - 0.9) / 0.25)
        rr = 60 + 10 * math.sin(t * 6)
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=BLUE + (int(255 * aa),), width=6)
        label(d, "가운데만 제자리", W / 2, 1230, int(60 * (0.6 + 0.4 * back((t - 0.9) / 0.3))), BLUE, anchor="mm", a=aa)
    return im.convert("RGB")

SCENES = {"wave": wave, "spots": spots, "turn": turn, "center": center}

if __name__ == "__main__":
    fn = SCENES[sys.argv[1]]; out = sys.argv[2]
    if out.endswith(".jpg"):
        ims = [fn(float(v)).resize((270, 480), Image.LANCZOS) for v in sys.argv[3:]]
        s = Image.new("RGB", (270 * len(ims), 480)); [s.paste(m, (i * 270, 0)) for i, m in enumerate(ims)]
        s.save(out, quality=85); raise SystemExit
    D = float(sys.argv[3]); tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(D * FPS))):
        p.stdin.write(fn(n / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, out); print("ok", out)
