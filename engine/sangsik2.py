"""1분 상식 2편 - 비행기 창문의 작은 구멍 (27 s, 1080x1920, 30 fps)."""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 27.0
OUT = os.path.dirname(os.path.abspath(__file__))
IY0, IH, SC = 260, 1000, 2            # illustration band (frame y 260..1260), drawn at 2x


def kr(path):
    for i in range(8):
        try:
            if "KR" in ImageFont.truetype(path, 20, index=i).getname()[0]:
                return i
        except Exception:
            break
    raise SystemExit("no KR face in " + path)


FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FM = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
IB, IM = kr(FB), kr(FM)
_f = {}
def F(size, black=True):
    k = (size, black)
    if k not in _f:
        _f[k] = ImageFont.truetype(FB if black else FM, max(2, size), index=IB if black else IM)
    return _f[k]


WHITE = (248, 249, 252); YEL = (255, 214, 64); BLUE = (90, 169, 255); INK = (14, 18, 34)
RED = (240, 72, 72); GREEN = (70, 205, 140); ORANGE = (255, 154, 61)
CABIN = (236, 226, 205); OUTSIDE = (22, 62, 118); DARKGAP = (26, 34, 58); FRAME = (150, 160, 180)


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def eio(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def mix(a, b, k):
    return tuple(int(a[i] + (b[i] - a[i]) * k) for i in range(3))


def make_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    img = np.zeros((H, W, 3), np.float32)
    top, bot = np.array((11, 16, 36), np.float32), np.array((16, 24, 54), np.float32)
    img += top + (bot - top) * (yy / H)[..., None]
    d = np.sqrt((xx - 540) ** 2 + (yy - 760) ** 2) / 1100
    img += (np.clip(1 - d, 0, 1) ** 2 * 0.22)[..., None] * np.array((60, 90, 200), np.float32)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


BG = make_bg()
BG_ILL = BG.crop((0, IY0, W, IY0 + IH)).resize((W * SC, IH * SC), Image.BILINEAR)
_sky = np.zeros((IH * SC, W * SC, 3), np.float32)
_k = (np.arange(IH * SC) / (IH * SC))[:, None, None]
_sky += np.array((70, 160, 240), np.float32) * (1 - _k) + np.array((196, 230, 255), np.float32) * _k
SKY = Image.fromarray(_sky.astype(np.uint8))


# ───────── drawing helpers on the 2x illustration canvas ─────────
def cxy(cam, wx, wy):
    s, fx, fy = cam
    return ((wx - fx) * s + 540) * SC, ((wy - fy) * s + 760 - IY0) * SC


def rr(d, cam, x0, y0, x1, y1, r, fill=None, outline=None, width=0):
    X0, Y0 = cxy(cam, x0, y0); X1, Y1 = cxy(cam, x1, y1)
    if X1 - X0 < 2 or Y1 - Y0 < 2:
        return
    rad = min(r * cam[0] * SC, (X1 - X0) / 2, (Y1 - Y0) / 2)
    d.rounded_rectangle((X0, Y0, X1, Y1), rad, fill=fill, outline=outline, width=max(1, int(width * cam[0] * SC)) if outline else 0)


def circ(d, cam, x, y, r, fill=None, outline=None, width=0):
    X, Y = cxy(cam, x, y); R = r * cam[0] * SC
    d.ellipse((X - R, Y - R, X + R, Y + R), fill=fill, outline=outline, width=max(1, int(width * cam[0] * SC)) if outline else 0)


def txt(d, cam, x, y, s, size, col, black=True, a=255):
    if a <= 3:
        return
    X, Y = cxy(cam, x, y)
    d.text((X, Y), s, font=F(int(size * SC * cam[0]), black), fill=col + (int(a),), anchor="mm")


def pill(d, cam, x, y, s, size, bg, fg, a=1.0, sc=1.0):
    if a <= 0.02 or sc <= 0.05:
        return
    f = F(int(size * SC * sc))
    w = d.textlength(s, font=f) / SC + 44 * sc; h = size * 1.75 * sc
    rr(d, cam, x - w / 2, y - h / 2, x + w / 2, y + h / 2, h / 2, fill=bg + (int(255 * a),))
    X, Y = cxy(cam, x, y)
    d.text((X, Y - 2 * SC), s, font=f, fill=fg + (int(255 * a),), anchor="mm")


# ───────── front view of the cabin window ─────────
HOLE = (540, 992)
CLOUDS = [(0, 560, 70, 34), (260, 700, 95, 22), (520, 860, 60, 44), (140, 930, 80, 28), (420, 500, 55, 38)]


def front(t, cam, fog=0.0, ring=False):
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA")
    rr(d, cam, 70, 280, 1010, 1240, 70, fill=(232, 236, 242))
    for yy in (330, 1190):                                   # panel seams
        rr(d, cam, 110, yy, 970, yy + 4, 2, fill=(208, 214, 224))
    rr(d, cam, 288, 398, 792, 1082, 232, fill=(206, 212, 223))
    rr(d, cam, 312, 422, 768, 1058, 208, fill=(170, 180, 196))
    sky = SKY.copy(); sd = ImageDraw.Draw(sky, "RGBA")
    for x0, y, sz, sp in CLOUDS:
        x = ((x0 - sp * t) % 760) + 180
        for dx, dy, k in ((0, 0, 1.0), (-0.7, 0.18, 0.7), (0.75, 0.15, 0.78), (0.1, -0.35, 0.72)):
            X, Y = cxy(cam, x + dx * sz, y + dy * sz); R = sz * k * cam[0] * SC
            sd.ellipse((X - R * 1.25, Y - R * 0.72, X + R * 1.25, Y + R * 0.72), fill=(255, 255, 255, 235))
    mask = Image.new("L", im.size, 0); md = ImageDraw.Draw(mask)
    rr(md, cam, 330, 440, 750, 1040, 190, fill=255)
    im.paste(sky, (0, 0), mask)
    if fog > 0.01:
        im.paste(Image.new("RGB", im.size, (238, 243, 248)), (0, 0), mask.point(lambda v: int(v * fog)))
        for i in range(9):                                   # moisture drifting to the hole
            ang = i * 0.7 + 0.4; r0 = 150 + 25 * (i % 3)
            k = eio((1 - fog / 0.82) * 1.15 - i * 0.02)
            px = HOLE[0] + math.cos(ang) * r0 * (1 - k); py = HOLE[1] - 40 - abs(math.sin(ang)) * r0 * 1.3 * (1 - k) + 40 * k
            circ(d, cam, px, py, 7 * (1 - 0.6 * k), fill=(150, 200, 245, int(230 * min(1, fog * 3))))
    rr(d, cam, 330, 440, 750, 1040, 190, outline=(120, 132, 152, 255), width=3)
    X0, Y0 = cxy(cam, 372, 520); X1, Y1 = cxy(cam, 420, 640)  # glass glint
    d.line((X0, Y1, X1, Y0), fill=(255, 255, 255, 110), width=int(10 * cam[0] * SC))
    circ(d, cam, HOLE[0], HOLE[1], 9.5, fill=(108, 120, 142))
    circ(d, cam, HOLE[0], HOLE[1], 5.5, fill=(24, 30, 46))
    if ring:
        for ph in (0.0, 0.5):
            p = (t * 1.1 + ph) % 1
            circ(d, cam, HOLE[0], HOLE[1], 14 + 30 * p, outline=YEL + (int(255 * (1 - p) ** 1.3),), width=5)
    return im


# ───────── cross-section: three panes ─────────
TOP, BOT, HOLE_Y = 440, 1060, 985
PATH = [(900, 1043), (690, 1043), (640, 1043), (598, 1010), (552, HOLE_Y), (512, HOLE_Y), (474, 950), (470, 800), (470, 620), (470, 500)]
_seg = [math.dist(PATH[i], PATH[i + 1]) for i in range(len(PATH) - 1)]
_tot = sum(_seg)


def along(u):
    dist = u * _tot
    for i, L in enumerate(_seg):
        if dist <= L:
            k = dist / L
            return PATH[i][0] + (PATH[i + 1][0] - PATH[i][0]) * k, PATH[i][1] + (PATH[i + 1][1] - PATH[i][1]) * k
        dist -= L
    return PATH[-1]


def pane(d, cam, x, w, y0, y1, bulge, col, lo=TOP, hi=BOT, outline=None):
    n = 22; L = []; R = []
    for i in range(n + 1):
        y = y0 + (y1 - y0) * i / n
        off = -bulge * math.sin(math.pi * (y - lo) / (hi - lo))
        L.append(cxy(cam, x - w / 2 + off, y)); R.append(cxy(cam, x + w / 2 + off, y))
    d.polygon(L + R[::-1], fill=col)
    if outline:
        d.line(L + R[::-1] + [L[0]], fill=outline, width=int(5 * SC), joint="curve")


def arrow(d, cam, xt, y, L, col, a=1.0, wd=15):
    if a <= 0.02:
        return
    c = col + (int(255 * a),)
    X0, Y = cxy(cam, xt + 26, y); X1, _ = cxy(cam, xt + L, y)
    d.line((X0, Y, X1, Y), fill=c, width=int(wd * SC))
    d.polygon([cxy(cam, xt, y), cxy(cam, xt + 34, y - 24), cxy(cam, xt + 34, y + 24)], fill=c)


def section(t):
    shake = 9 * math.sin(t * 55) * max(0, 1 - (t - 17.3) / 0.45) if t >= 17.3 else 0
    cam = (1.0, 540 + shake, 760)
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA")
    sp = ease((t - 6.0) / 0.8)
    xo, xm, xi = 540 - 140 * sp, 540, 540 + 120 * sp
    gapfill = eio((t - 13.9) / 1.5)
    cracked = t >= 17.3
    # regions
    rr(d, cam, 60, 330, xo, 1170, 44, fill=OUTSIDE); rr(d, cam, max(60, xo - 60), 330, xo, 1170, 0, fill=OUTSIDE)
    rr(d, cam, xm, 330, 1020, 1170, 44, fill=CABIN); rr(d, cam, xm, 330, xm + 60, 1170, 0, fill=CABIN)
    for cx_, cy_, r_ in ((150, 420, 26), (250, 1090, 34), (120, 900, 20)):
        circ(d, cam, cx_, cy_, r_, fill=(255, 255, 255, 26)); circ(d, cam, cx_ + r_ * 1.1, cy_ + 6, r_ * 0.8, fill=(255, 255, 255, 26))
    rr(d, cam, xo, TOP, xm, BOT, 0, fill=mix(DARKGAP, CABIN, gapfill))
    rr(d, cam, xo - 26, TOP - 38, xi + 18, TOP + 2, 10, fill=FRAME)
    rr(d, cam, xo - 26, BOT - 2, xi + 18, BOT + 38, 10, fill=FRAME)
    # bulges
    press_mid = ease((t - 11.2) / 0.5) * (1 - gapfill)
    back_mid = ease((t - 17.6) / 0.4) if cracked else 0
    b_mid = 9 * press_mid + 9 * back_mid
    b_out = 15 * ease((t - 15.0) / 0.5) * (1 - 0.6 * back_mid)
    glow_o = ease((t - 15.2) / 0.4) if not cracked else 0
    pane(d, cam, xi, 10, 472, 1028, 0, (222, 234, 244))
    pane(d, cam, xm, 22, TOP, HOLE_Y - 11, b_mid, (150, 205, 245), outline=GREEN + (int(255 * back_mid),) if back_mid > 0.05 else None)
    pane(d, cam, xm, 22, HOLE_Y + 11, BOT, b_mid, (150, 205, 245))
    pane(d, cam, xo, 30, TOP, BOT, b_out, (196, 228, 255), outline=YEL + (int(255 * glow_o),) if glow_o > 0.05 else None)
    if cracked:                                              # crack grows on the outer pane
        k = ease((t - 17.3) / 0.35)
        zz = [(xo - 4 - b_out, 640), (xo + 9 - b_out, 672), (xo - 10 - b_out, 706), (xo + 8 - b_out, 742), (xo - 7 - b_out, 778), (xo + 6 - b_out, 812), (xo - 3 - b_out, 846)]
        n = max(2, int(len(zz) * k + 0.999))
        d.line([cxy(cam, *p) for p in zz[:n]], fill=RED + (255,), width=int(7 * SC), joint="curve")
    # labels for the three panes (scene 3)
    la = 1 - ease((t - 8.7) / 0.3)
    for i, (x, name, t0) in enumerate(((xo, "바깥 창", 6.9), (xm, "가운데 창", 7.3), (xi, "안쪽 덮개", 7.7))):
        k = back((t - t0) / 0.3) if t >= t0 else 0
        if k > 0 and la > 0.02:
            lx = x + (-70, 0, 78)[i]
            circ(d, cam, x, 368, 30 * k, fill=YEL + (int(255 * la),))
            txt(d, cam, x, 365, str(i + 1), 40 * k, INK, a=255 * la)
            pill(d, cam, lx, 1135, name, 34, (255, 255, 255), INK, a=la, sc=k)
    # region names + outside pressure (scene 4)
    ra = ease((t - 9.0) / 0.3) * (1 - ease((t - 19.7) / 0.3))
    txt(d, cam, 215, 380, "바깥", 40, WHITE, a=255 * ra)
    txt(d, cam, 850, 380, "기내", 40, INK, a=255 * ra)
    qa = ease((t - 9.3) / 0.3) * (1 - ease((t - 12.9) / 0.3))
    if qa > 0.02:
        k = back((t - 9.3) / 0.35)
        txt(d, cam, 215, 665, "기압", 40, (190, 215, 250), a=255 * qa)
        txt(d, cam, 215, 770, "1/4", 120 * k, YEL, a=255 * qa)
    # cabin air pushing (scene 4b)
    osc = 9 * math.sin(t * 7)
    pa = ease((t - 11.0) / 0.3)
    if pa > 0.02:
        for y in (560, 720, 880):
            arrow(d, cam, xi + 30 + osc, y, 190, ORANGE, a=pa)
            arrow(d, cam, xm + 20 + osc * 0.6, y, 78, ORANGE, a=pa * (1 - gapfill) * (1 if not cracked else 0), wd=11)
    if cracked and back_mid > 0.02:
        for y in (560, 720, 880):
            arrow(d, cam, xm + 22 + osc * 0.6, y, 78, ORANGE, a=back_mid, wd=11)
    # air through the hole (scene 5)
    fa = ease((t - 13.2) / 0.4) * (1 - ease((t - 16.7) / 0.3))
    if fa > 0.02:
        for ph in (0.0, 0.5):
            p = (t * 1.1 + ph) % 1
            circ(d, cam, xm, HOLE_Y, 16 + 26 * p, outline=YEL + (int(255 * fa * (1 - p)),), width=5)
        for i in range(16):
            u = ((t - 13.2) * 0.42 + i / 16) % 1
            if (t - 13.2) * 0.42 + i / 16 < 1 and u > (t - 13.2) * 0.42:
                continue
            x, y = along(u)
            circ(d, cam, x, y, 8, fill=ORANGE + (int(255 * fa),))
    oa = ease((t - 15.0) / 0.3) * (1 - back_mid)
    if oa > 0.02:
        for y in (560, 720, 880):
            arrow(d, cam, xo + 24 + osc * 0.6, y, 86, ORANGE, a=oa, wd=11)
    # callouts
    if 15.4 <= t < 17.3:
        pill(d, cam, 215, 720, "여기가 버팀", 36, YEL, INK, sc=back((t - 15.4) / 0.3))
    if t >= 17.45:
        pill(d, cam, 215, 720, "금이 가도", 36, RED, WHITE, sc=back((t - 17.45) / 0.3))
    if t >= 18.0:
        pill(d, cam, 845, 1105, "가운데 창이 버팀", 36, GREEN, INK, sc=back((t - 18.0) / 0.3))
    return im


# ───────── timeline ─────────
def cam_front(t):
    if t < 5.6:
        k = eio((t - 1.2) / 0.9)
        return (1.1 + 0.08 * min(t, 1.2) / 1.2 + 1.62 * k + 0.25 * max(0, t - 2.1) / 3.5, 540, 740 + (HOLE[1] - 740) * k)
    if t < 23.0:
        return (1.45 + 0.05 * (t - 20) / 3, 540, 790)
    k = eio((t - 23.0) / 1.6)
    return (1.5 - 0.4 * k, 540, 790 - 50 * k)


def illus(t):
    def scene(tt):
        if tt < 5.6:
            return front(tt, cam_front(tt), ring=tt > 1.9)
        if tt < 20.0:
            return section(tt)
        if tt < 23.0:
            return front(tt, cam_front(tt), fog=0.82 * (1 - eio((tt - 20.3) / 2.0)))
        return front(tt, cam_front(tt), ring=tt > 23.5)
    for cut in (5.6, 20.0):
        if cut <= t < cut + 0.26:
            return Image.blend(scene(cut - 0.001), scene(t), eio((t - cut) / 0.26))
    return scene(t)


Y_, W_ = YEL, WHITE
CAPS = [
    (0.0, 1.4, [("이거", W_)], [("알고 있었나요?", Y_)]),
    (1.4, 3.6, [("비행기 창문에", W_)], [("구멍", Y_), ("이 뚫려 있다?", W_)]),
    (3.6, 5.6, [("창문 아래쪽", W_)], [("바늘구멍", Y_), ("만 한 이 구멍", W_)]),
    (5.6, 9.0, [("창문은 한 장이 아니라", W_)], [("세 장", Y_), ("입니다", W_)]),
    (9.0, 11.0, [("하늘 위 바깥 기압은", W_)], [("땅의 ", W_), ("4분의 1", Y_)]),
    (11.0, 13.0, [("기내 공기가 창문을", W_)], [("바깥으로 ", W_), ("밀어냅니다", Y_)]),
    (13.0, 17.0, [("구멍으로 공기가 통해서", W_)], [("힘은 ", W_), ("바깥 창", Y_), ("이 받습니다", W_)]),
    (17.0, 20.0, [("가운데 창은", W_)], [("만일을 위한 ", W_), ("예비", Y_)]),
    (20.0, 23.0, [("덤으로 습기가 빠져", W_)], [("김", Y_), ("도 덜 서립니다", W_)]),
    (23.0, 25.0, [("다음에 타면", W_)], [("꼭 ", W_), ("찾아보세요", Y_)]),
    (25.0, 27.0, [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)]),
]
_lc = {}
def line_img(segs, size=84):
    k = (tuple(segs), size)
    if k not in _lc:
        f = F(size); st = 9
        tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
        ws = [tmp.textlength(s, font=f) for s, _ in segs]
        im = Image.new("RGBA", (int(sum(ws)) + st * 2 + 8, int(size * 1.5) + st * 2), (0, 0, 0, 0))
        d = ImageDraw.Draw(im); x = st + 4
        for (s, c), w in zip(segs, ws):
            d.text((x, im.height // 2), s, font=f, fill=c, anchor="lm", stroke_width=st, stroke_fill=(6, 8, 18))
            x += w
        _lc[k] = im
    return _lc[k]


def put(base, layer, cx, cy, a=1.0, sc=1.0):
    if a <= 0.01:
        return
    if abs(sc - 1) > 0.004:
        layer = layer.resize((max(2, int(layer.width * sc)), max(2, int(layer.height * sc))), Image.BILINEAR)
    if a < 0.995:
        layer = layer.copy(); layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    base.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


def box_img(text, size, bg, fg, pad=30, rot=0):
    k = ("box", text, size, bg, fg, rot)
    if k not in _lc:
        f = F(size); w = int(ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(text, font=f))
        h = int(size * 1.7)
        im = Image.new("RGBA", (w + pad * 2, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, im.width - 1, h - 1), h // 2 if rot == 0 else 18, fill=bg + (255,))
        d.text((im.width // 2, h // 2 - 3), text, font=f, fill=fg, anchor="mm")
        _lc[k] = im.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else im
    return _lc[k]


ILL_MASK = Image.new('L', (W, IH), 0)
ImageDraw.Draw(ILL_MASK).rounded_rectangle((24, 0, W - 25, IH - 1), 56, fill=255)
HEAD = None
def header():
    global HEAD
    if HEAD is None:
        HEAD = Image.new("RGBA", (W, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(HEAD)
        f = F(80); w = d.textlength("1분 상식", font=f)
        d.rounded_rectangle((540 - w / 2 - 54, 2, 540 + w / 2 + 54, 120), 59, fill=YEL + (255,))
        d.text((540, 57), "1분 상식", font=f, fill=INK, anchor="mm")
    return HEAD


def frame(t):
    im = BG.copy()
    im.paste(illus(t).reduce(SC), (0, IY0), ILL_MASK)
    im = im.convert("RGBA")
    im.alpha_composite(header(), (0, 92))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((90, 236, 990, 243), 3, fill=(255, 255, 255, 40))
    d.rounded_rectangle((90, 236, 90 + 900 * min(1, t / DUR), 243), 3, fill=YEL + (255,))
    if 2.6 <= t < 3.6:                                       # "일부러요" stamp
        k = back((t - 2.6) / 0.22); a = 1 - ease((t - 3.4) / 0.2)
        put(im, box_img("일부러요!", 92, RED, WHITE, pad=40, rot=7), 540, 500, a, 0.6 + 0.4 * k)
    if 3.9 <= t < 5.6:                                       # name tag for the hole
        k = back((t - 3.9) / 0.25); a = 1 - ease((t - 5.4) / 0.2)
        d.line((566, 742, 566 + 150 * min(1, k), 742 - 150 * min(1, k)), fill=YEL + (int(255 * a),), width=7)
        put(im, box_img("이름은 ‘블리드 홀’", 46, (255, 255, 255), INK), 760, 560, a, 0.6 + 0.4 * k)
    if t >= 25.2:
        k = back((t - 25.2) / 0.28)
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1212, 1.0, 0.6 + 0.4 * k)
    for t0, t1, l1, l2 in CAPS:
        if t0 <= t < t1:
            a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if t1 < DUR else 1
            for i, (segs, cy) in enumerate(((l1, 1352), (l2, 1464))):
                lt = t - t0 - i * 0.13
                if lt < 0:
                    continue
                put(im, line_img(segs), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
    return im.convert("RGB")



# ───────── v3: signature lockup, fixed episode title, kinetic hook ─────────
SHIFT = 40
EP_TITLE = (("비행기 창문의 ", WHITE), ("구멍", YEL), (", 왜 있을까?", WHITE))


def signature(im, t):
    """Channel signature: a 1-minute timer ring that fills as the video plays + wordmark."""
    S2 = 2; L = Image.new("RGBA", (W * S2, 300 * S2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    f = F(138 * S2); wt = d.textlength("상식", font=f) / S2
    R, gap = 90, 30; total = 2 * R + gap + wt; x0 = 540 - total / 2; cx, cy = x0 + R, 150
    q = lambda *v: tuple(int(a * S2) for a in v)
    d.rounded_rectangle(q(cx - 13, cy - R - 20, cx + 13, cy - R + 4), 6 * S2, fill=YEL + (255,))
    d.ellipse(q(cx - R, cy - R, cx + R, cy + R), fill=(22, 30, 62, 255), outline=(255, 255, 255, 70), width=12 * S2)
    d.arc(q(cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * min(1, max(0.02, t / DUR)), fill=YEL + (255,), width=15 * S2)
    d.text(q(cx, cy - 5), "1분", font=F(84 * S2), fill=YEL, anchor="mm")
    d.text(q(x0 + 2 * R + gap, cy - 12), "상식", font=f, fill=WHITE, anchor="lm", stroke_width=8 * S2, stroke_fill=(6, 8, 18))
    d.rounded_rectangle(q(x0 + 2 * R + gap + 4, cy + 76, x0 + total - 4, cy + 90), 7 * S2, fill=YEL + (255,))
    L = L.resize((W, 300), Image.LANCZOS)
    k = back(t / 0.3) if t < 0.3 else 1.0
    put(im, L, 540, 150, 1.0, 0.7 + 0.3 * k)
    if EP_TITLE: put(im, line_img(EP_TITLE, 56), 540, 246, ease((t - 0.1) / 0.2) if t < 0.4 else 1.0)


def kinetic(im, t, t0, t1, rows, ys, size, stagger=0.13, slam=0.7, out=0.13):
    """Words slam in one by one; yellow words keep pulsing."""
    if not (t0 <= t < t1):
        return
    a_out = 1 - ease((t - (t1 - out)) / out)
    f = F(size); tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); idx = 0
    for words, cy in zip(rows, ys):
        ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) for w in words]
        sp = size * 0.26; x = 540 - (sum(ws) + sp * (len(ws) - 1)) / 2
        for w, ww in zip(words, ws):
            lt = t - t0 - idx * stagger; idx += 1
            if lt >= 0:
                sc = 1 + slam * (1 - ease(lt / 0.17))
                if any(c == YEL for _, c in w):
                    sc *= 1 + 0.04 * math.sin(t * 15)
                put(im, line_img(tuple(w), size), x + ww / 2, cy, ease(lt / 0.07) * a_out, sc)
            x += ww + sp


def frame(t):
    im = BG.copy()
    im.paste(illus(t).reduce(SC), (0, IY0 + SHIFT), ILL_MASK)
    im = im.convert("RGBA")
    signature2(im, t)
    d = ImageDraw.Draw(im)
    if t < 1.52:                                             # dim the picture behind the opening question
        a = min(1, t / 0.08) * (1 - ease((t - 1.36) / 0.14))
        ov = Image.new("RGBA", (W, IH), (8, 12, 28, 255)); ov.putalpha(ILL_MASK.point(lambda v: int(v * 0.49 * a)))
        im.alpha_composite(ov, (0, IY0 + SHIFT))
    kinetic(im, t, 0.0, 1.5, [[[("이거", WHITE)]], [[("알고", YEL)], [("있었나요?", YEL)]]], (690, 850), 128, stagger=0.17, slam=0.9)
    kinetic(im, t, 1.4, 3.6, [[[("비행기", WHITE)], [("창문에", WHITE)]], [[("구멍", YEL), ("이", WHITE)], [("뚫려", WHITE)], [("있다?", WHITE)]]], (1388, 1500), 84, stagger=0.12, slam=0.5)
    if 2.6 <= t < 3.6:
        k = back((t - 2.6) / 0.22); a = 1 - ease((t - 3.4) / 0.2)
        put(im, box_img("일부러요!", 92, RED, WHITE, pad=40, rot=7), 540, 540, a, 0.6 + 0.4 * k)
    if 3.9 <= t < 5.6:
        k = back((t - 3.9) / 0.25); a = 1 - ease((t - 5.4) / 0.2)
        d.line((566, 782, 566 + 150 * min(1, k), 782 - 150 * min(1, k)), fill=YEL + (int(255 * a),), width=7)
        put(im, box_img("이름은 ‘블리드 홀’", 46, (255, 255, 255), INK), 760, 600, a, 0.6 + 0.4 * k)
    if t >= 25.2:
        k = back((t - 25.2) / 0.28)
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1252, 1.0, 0.6 + 0.4 * k)
    for t0, t1, l1, l2 in CAPS[2:]:
        if t0 <= t < t1:
            a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if t1 < DUR else 1
            for i, (segs, cy) in enumerate(((l1, 1388), (l2, 1500))):
                lt = t - t0 - i * 0.13
                if lt < 0:
                    continue
                put(im, line_img(tuple(segs)), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
    return im.convert("RGB")



# ───────── v4: display-font signature (previous size) ─────────
SIG = os.environ.get("SIG", "A")
SIG_FONT = {"A": "black-han-sans", "B": "bagel-fat-one", "C": "gasoek-one", "D": "jua", "E": "do-hyeon"}
SLICE = {"분": 117, "식": 117, "상": 118, "1": 119}
_df = {}
def DF(ch, size):
    k = (SIG, ch, size)
    if k not in _df:
        _df[k] = ImageFont.truetype(f"{os.path.dirname(OUT)}/assets/fonts/{SIG_FONT[SIG]}-{SLICE[ch]}.ttf", size)
    return _df[k]
def dtext(d, x, y, s, size, fill, track=0.0):
    """Draw s left-aligned at x, vertically centred on y, one glyph at a time. Returns end x."""
    for ch in s:
        if ch == " ":
            x += size * 0.25; continue
        f = DF(ch, size); d.text((x, y), ch, font=f, fill=fill, anchor="lm"); x += d.textlength(ch, font=f) + size * track
    return x
def dwidth(d, s, size, track=0.0):
    return sum(size * 0.25 if ch == " " else d.textlength(ch, font=DF(ch, size)) + size * track for ch in s)


def signature2(im, t):
    S2 = 2; L = Image.new("RGBA", (W * S2, 220 * S2), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    size = 104 * S2; wt = dwidth(d, "상식", size, 0.04) / S2
    R, gap, px = 64, 34, 26; total = 2 * R + gap + wt + px * 2; x0 = 540 - total / 2; cx, cy = x0 + R, 110
    q = lambda *v: tuple(int(a * S2) for a in v)
    d.rounded_rectangle(q(cx - 10, cy - R - 16, cx + 10, cy - R + 4), 5 * S2, fill=YEL + (255,))
    d.ellipse(q(cx - R, cy - R, cx + R, cy + R), fill=(22, 30, 62, 255), outline=(255, 255, 255, 70), width=9 * S2)
    d.arc(q(cx - R, cy - R, cx + R, cy + R), -90, -90 + 360 * min(1, max(0.02, t / DUR)), fill=YEL + (255,), width=11 * S2)
    w1 = dwidth(d, "1분", 58 * S2); dtext(d, cx * S2 - w1 / 2, (cy - 2) * S2, "1분", 58 * S2, YEL)
    # tilted yellow plate with the word in dark ink (sticker look)
    pw, ph = int((wt + px * 2) * S2), 124 * S2
    P = Image.new("RGBA", (pw + 24, ph + 24), (0, 0, 0, 0)); pd = ImageDraw.Draw(P)
    pd.rounded_rectangle((16, 18, pw + 16, ph + 18), 26 * S2 // 2 * 2, fill=(0, 0, 0, 110))
    pd.rounded_rectangle((4, 4, pw + 4, ph + 4), 26 * S2 // 2 * 2, fill=YEL + (255,))
    dtext(pd, 4 + px * S2, 4 + ph / 2 - 2 * S2, "상식", size, INK, 0.04)
    P = P.rotate(3.5, expand=True, resample=Image.BICUBIC)
    L.alpha_composite(P, (int((x0 + 2 * R + gap) * S2) - (P.width - pw) // 2, int(cy * S2 - P.height / 2)))
    L = L.resize((W, 220), Image.LANCZOS)
    k = back(t / 0.3) if t < 0.3 else 1.0
    put(im, L, 540, 128, 1.0, 0.7 + 0.3 * k)
    if EP_TITLE: put(im, line_img(EP_TITLE, 56), 540, 246, ease((t - 0.1) / 0.2) if t < 0.4 else 1.0)


# ───────── sound effects ─────────
def sfx(path):
    sr = 44100; n = int(DUR * sr); x = np.zeros(n); rng = np.random.default_rng(3)
    def add(at, sig):
        i = int(at * sr); sig = sig[: max(0, n - i)]; x[i:i + len(sig)] += sig
    def env(m, d): return np.exp(-np.arange(m) / sr / d)
    def pop(at, f0=620, vol=.22):
        m = int(.12 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * (f0 + 380 * np.exp(-tt * 40)) * tt) * env(m, .03))
    def whoosh(at, ln=.38, vol=.2):
        m = int(ln * sr); z = rng.standard_normal(m); y = np.zeros(m); s = 0.0
        a = np.linspace(.02, .35, m)
        for i in range(m):
            s += a[i] * (z[i] - s); y[i] = s
        add(at - ln * .6, vol * 3 * y * np.sin(np.pi * np.arange(m) / m) ** 2)
    def ding(at, f=1320, vol=.2, d=.22):
        m = int(.7 * sr); tt = np.arange(m) / sr
        add(at, vol * (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.01 * tt)) * env(m, d))
    def thud(at, vol=.5):
        m = int(.25 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-tt * 30)) / sr) * env(m, .07) + .25 * rng.standard_normal(m) * env(m, .006))
    for t0, *_ in CAPS:
        pop(t0 + .02)
    pop(.17, 760, .22); pop(.34, 920, .26); pop(1.52, 700, .18); pop(1.64, 780, .18); pop(1.76, 860, .18); whoosh(1.5, .3, .16); ding(2.0, 1568, .16); thud(2.6); pop(3.9, 900, .2)
    whoosh(5.6); whoosh(20.0); whoosh(23.0)
    for i, tt in enumerate((6.9, 7.3, 7.7)):
        pop(tt, 700 + 160 * i, .26)
    ding(9.3, 880, .16)
    m = int(2.6 * sr); h = np.diff(rng.standard_normal(m), prepend=0) * np.sin(np.pi * np.arange(m) / m) ** 1.5
    add(13.2, .05 * h)
    ding(15.2, 1175, .15)
    m = int(.3 * sr); add(17.3, .5 * np.diff(rng.standard_normal(m), prepend=0) * env(m, .035)); thud(17.3, .45)
    ding(18.0, 1047, .16); ding(18.14, 1568, .16)
    ding(25.2, 1319, .16); ding(25.34, 1760, .16)
    x = np.tanh(x * 1.3) * .9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ts = [float(v) for v in sys.argv[3:]]
        ims = [frame(tt).resize((360, 640), Image.LANCZOS) for tt in ts]
        s = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            s.paste(im, (i * 360, 0))
        s.save(f"{OUT}/{sys.argv[2]}.jpg", quality=88)
    elif sys.argv[1] == "one":
        frame(float(sys.argv[3])).save(f"{OUT}/{sys.argv[2]}.jpg", quality=90)
    else:
        music, final = sys.argv[2], sys.argv[3]
        sfx(f"{OUT}/s2_sfx.wav"); tmp = f"{OUT}/s2.part.mp4"
        fo = DUR - 0.8
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-i", music, "-i", f"{OUT}/s2_sfx.wav",
                              "-filter_complex", f"[1:a]atrim=0:{DUR},volume=-9dB,afade=t=in:d=0.05,afade=t=out:st={fo}:d=0.8[m];[2:a]volume=0dB[s];[m][s]amix=inputs=2:normalize=0[a]",
                              "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, final); print("ok", final)
