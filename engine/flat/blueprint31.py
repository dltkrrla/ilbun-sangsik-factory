"""31편 6번째 장면: 옛날 콜라병 받침을 설계도(블루프린트) 모션그래픽으로.
둥근 바닥 병을 선으로 그리고 → 흔들려서 못 서는 걸 보여주고 → 받침이 아래에서 올라와 딱 끼워지면 멈춘다.
usage: python3 blueprint31.py out.mp4"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, D = 1080, 1920, 30, 4.5
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FREG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
def F(s, reg=False):
    return ImageFont.truetype(FREG if reg else FONT, s, index=1)

BG = (14, 48, 92); LINE = (226, 244, 255); CYAN = (120, 210, 255); YEL = (255, 214, 64); RED = (255, 110, 90)

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# 배경: 모눈 + 비네트
GRID = Image.new("RGB", (W, H), BG)
g = ImageDraw.Draw(GRID)
for x in range(0, W, 40):
    g.line((x, 0, x, H), fill=(30, 74, 124) if x % 200 else (52, 104, 160), width=1 if x % 200 else 2)
for y in range(0, H, 40):
    g.line((0, y, W, y), fill=(30, 74, 124) if y % 200 else (52, 104, 160), width=1 if y % 200 else 2)
vig = Image.new("L", (W, H), 0); ImageDraw.Draw(vig).ellipse((-300, -200, W + 300, H + 200), fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(160))
GRID = Image.composite(GRID, Image.new("RGB", (W, H), (6, 22, 46)), vig)

# 병 외곽선 (중심 x=540, 바닥 반구 중심 y=1040, 반지름 190)
CX, BY, R = 540, 1040, 190
def bottle_path():
    pts = []
    pts += [(470, 300), (470, 352), (492, 352), (492, 400)]                    # 뚜껑·목(왼쪽)
    for i in range(13):                                                         # 어깨(왼쪽)
        a = i / 12; pts.append((492 - (492 - (CX - R)) * ease(a), 400 + 90 * a))
    pts.append((CX - R, BY))                                                    # 몸통(왼쪽)
    for i in range(1, 37):                                                      # 둥근 바닥
        a = math.pi - math.pi * i / 36; pts.append((CX + R * math.cos(a), BY + R * math.sin(a)))
    for i in range(13):                                                         # 어깨(오른쪽)
        a = 1 - i / 12; pts.append((588 + ((CX + R) - 588) * ease(a), 400 + 90 * a))
    pts += [(588, 400), (588, 352), (610, 352), (610, 300), (470, 300)]
    return pts
PATH = bottle_path()
SEG = [math.dist(PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)]; TOT = sum(SEG)

def partial(pts, f):
    if f >= 1: return pts
    out = [pts[0]]; left = TOT * f
    for i, s in enumerate(SEG):
        if left <= s:
            a = left / s if s else 0
            out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * a, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * a)); break
        out.append(pts[i + 1]); left -= s
    return out

def bottle_layer(f):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    p = partial(PATH, f)
    if len(p) > 1:
        d.line(p, fill=LINE + (255,), width=7, joint="curve")
    if f > 0.98:                                                                # 액체선·중심선
        d.line((CX - R + 20, 560, CX + R - 20, 560), fill=CYAN + (150,), width=3)
        for y in range(330, 1260, 36):
            d.line((CX, y, CX, y + 18), fill=CYAN + (110,), width=2)
    return L

CUP_TOP, CUP_BOT, CUP_W = 1085, 1255, 430
GROUND = CUP_BOT                       # 바닥(식탁) 선
LIFT = 170                              # 받침을 끼우려고 병을 들어 올리는 높이

def cup_layer(offx):
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x0, x1 = CX - CUP_W // 2 + offx, CX + CUP_W // 2 + offx
    m = Image.new("L", (W, H), 0); md = ImageDraw.Draw(m)
    md.rounded_rectangle((x0, CUP_TOP, x1, CUP_BOT), 18, fill=255)
    md.ellipse((CX + offx - R - 4, BY - R - 4, CX + offx + R + 4, BY + R + 4), fill=0)     # 반구 모양으로 파인 윗면
    hatch = Image.new("RGBA", (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hatch)
    for k in range(-H, W + H, 26):
        hd.line((k, CUP_BOT + 10, k + (CUP_BOT - CUP_TOP + 20), CUP_TOP - 10), fill=YEL + (120,), width=3)
    L.paste(hatch, (0, 0), m)
    edge = m.filter(ImageFilter.FIND_EDGES).point(lambda v: 255 if v > 40 else 0).filter(ImageFilter.MaxFilter(5))
    L.paste(Image.new("RGBA", (W, H), YEL + (255,)), (0, 0), edge)
    return L

def label(d, text, x, y, size, col, anchor="lm", a=1.0):
    if a <= 0: return
    c = col + (int(255 * a),)
    d.text((x, y), text, font=F(size), fill=c, anchor=anchor, stroke_width=6, stroke_fill=(8, 26, 52, int(255 * a)))

def ground(d, a):
    if a <= 0: return
    d.line((110, GROUND, 970, GROUND), fill=LINE + (int(200 * a),), width=4)
    for x in range(120, 970, 34):
        d.line((x, GROUND + 4, x - 22, GROUND + 26), fill=LINE + (int(90 * a),), width=2)

def frame(t):
    im = GRID.copy().convert("RGBA")
    a_grid = ease(t / 0.3)
    if a_grid < 1:
        im = Image.blend(Image.new("RGBA", (W, H), (6, 22, 46, 255)), im, a_grid)
    d = ImageDraw.Draw(im)
    label(d, "DWG. 31-B  |  옛날 2L 콜라병", 70, 250, 34, CYAN, a=ease((t - 0.1) / 0.3) * (1 - ease((t - 2.2) / 0.15)) + ease((t - 3.05) / 0.3) * (t > 3))
    ground(d, ease((t - 0.2) / 0.3))
    f = ease(t / 1.1)
    # 흔들림: 둥근 바닥이 식탁 위를 굴러가듯 좌우로 (1.2~2.3초), 그 뒤 멈춤
    rock = 0.0
    if t >= 1.2:
        amp = 10 * ease((t - 1.2) / 0.2) * (1 - ease((t - 2.0) / 0.3))
        rock = amp * math.sin((t - 1.2) * 2 * math.pi * 1.5)
    # 높이: 처음엔 바닥에 닿음(+25) → 들어 올림 → 받침 속으로 내려앉음(0)
    dy = (GROUND - (BY + R))
    dy += (-(GROUND - (BY + R)) - LIFT) * ease((t - 2.3) / 0.3)
    dy += LIFT * ease((t - 2.8) / 0.15)
    dx = -R * math.radians(rock)                    # 구르기: 기울어진 만큼 옆으로 이동
    B = bottle_layer(f)
    if abs(rock) > 0.05 or abs(dy) > 0.5:
        B = B.rotate(rock, resample=Image.BICUBIC, center=(CX, BY), translate=(dx, dy))
    # 받침: 옆에서 미끄러져 들어옴
    if t >= 2.4:
        offx = int(-(1 - ease((t - 2.4) / 0.4)) * 700)
        im.alpha_composite(cup_layer(offx))
    im.alpha_composite(B)
    d = ImageDraw.Draw(im)
    a1 = ease((t - 0.95) / 0.25) * (1 - ease((t - 2.2) / 0.2))
    if a1 > 0:
        d.line((CX + 150 + dx, BY + 120 + dy, 830, 1130), fill=CYAN + (int(255 * a1),), width=3)
        label(d, "둥근 바닥", 842, 1130, 50, LINE, a=a1)
    a2 = ease((t - 1.25) / 0.2) * (1 - ease((t - 2.25) / 0.2))
    if a2 > 0:
        for sgn in (-1, 1):
            cx0 = CX + sgn * 300
            d.arc((cx0 - 70, 640, cx0 + 70, 780), 200 if sgn < 0 else -20, 340 if sgn < 0 else 160, fill=RED + (int(255 * a2),), width=8)
        label(d, "흔들흔들", 890, 390, 46, RED, anchor="mm", a=a2)
        label(d, "혼자 못 서요", 890, 455, 46, RED, anchor="mm", a=a2)
    if t >= 2.95:
        k = ease((t - 2.95) / 0.15)
        flash = max(0.0, 1 - (t - 2.95) / 0.35)
        if flash > 0:
            d.ellipse((CX - 300 * k, 1110 - 120 * k, CX + 300 * k, 1110 + 120 * k), outline=YEL + (int(220 * flash),), width=6)
        label(d, "딱!", 860, 960, int(78 * (0.7 + 0.3 * back((t - 2.95) / 0.25))), YEL, anchor="mm", a=k)
        a3 = ease((t - 3.1) / 0.25)
        d.line((CX - CUP_W // 2 + 30, 1180, 200, 1180), fill=YEL + (int(255 * a3),), width=3)
        label(d, "받침", 70, 1180, 56, YEL, a=a3)
        a4 = ease((t - 3.4) / 0.3)
        label(d, "똑바로 선다!", 880, 420, 50, LINE, anchor="mm", a=a4)
    return im.convert("RGB")

if __name__ == "__main__":
    out = sys.argv[1]; tmp = out + ".part.mp4"
    if len(sys.argv) > 2:                                           # 미리보기: 시각들
        ims = [frame(float(v)).resize((270, 480), Image.LANCZOS) for v in sys.argv[2:]]
        s = Image.new("RGB", (270 * len(ims), 480)); [s.paste(m, (i * 270, 0)) for i, m in enumerate(ims)]
        s.save(out, quality=85); raise SystemExit
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(D * FPS))):
        p.stdin.write(frame(n / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, out); print("ok", out)
