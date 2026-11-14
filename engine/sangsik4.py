"""1분 상식 4편 - 맨홀 뚜껑은 왜 둥글까 (27 s). Reuses the episode-2 template (sangsik2.py)."""
import os, sys, math, subprocess, wave
os.environ.setdefault("SIG", "B")
import numpy as np
from PIL import Image, ImageDraw
import sangsik2 as b
from sangsik2 import *

DUR = 27.0
b.DUR = DUR
b.EP_TITLE = (("맨홀 뚜껑은 왜 ", WHITE), ("둥글까", YEL), ("?", WHITE))
ASPH, ASPH2 = (62, 66, 78), (70, 75, 88)
CONC, HOLE_C = (134, 138, 148), (10, 12, 20)
IRON, IRON_D, IRON_L = (92, 98, 112), (66, 70, 82), (128, 134, 150)
C0 = (1.0, 540, 760)


def lerp(a, b_, k): return a + (b_ - a) * k


def badge(d, cam, x, y, r, col, kind, k=1.0):
    if k <= 0.03:
        return
    r = r * k; circ(d, cam, x, y, r, fill=col + (255,))
    if kind == "x":
        for sx in (1, -1):
            d.line([cxy(cam, x - r * .42 * sx, y - r * .42), cxy(cam, x + r * .42 * sx, y + r * .42)], fill=(255, 255, 255, 255), width=int(r * .26 * SC))
    elif kind == "check":
        d.line([cxy(cam, x - r * .46, y + r * .02), cxy(cam, x - r * .12, y + r * .36), cxy(cam, x + r * .48, y - r * .34)], fill=(255, 255, 255, 255), width=int(r * .24 * SC), joint="curve")
    else:
        txt(d, cam, x, y - r * .06, "!", r * 1.3, WHITE)


def rbox(d, cam, cx, cy, L, T, ang, fill, outline=None):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in ((-L / 2, -T / 2), (L / 2, -T / 2), (L / 2, T / 2), (-L / 2, T / 2))]
    d.polygon([cxy(cam, *p) for p in pts], fill=fill, outline=outline)


def dashed(d, cam, p, q, col, wd=7, dash=26):
    n = max(1, int(math.dist(p, q) / dash))
    for i in range(0, n, 2):
        a = i / n; b_ = min(1, (i + 1) / n)
        d.line([cxy(cam, lerp(p[0], q[0], a), lerp(p[1], q[1], a)), cxy(cam, lerp(p[0], q[0], b_), lerp(p[1], q[1], b_))], fill=col, width=int(wd * SC))


def cover(d, cam, cx, cy, h, rad, ang=0.0, sc=1.0):
    """Top-down cast-iron cover. rad == h draws a circle, small rad a square."""
    h *= sc; rad *= sc
    rr(d, cam, cx - h - 6, cy - h + 10, cx + h + 6, cy + h + 16, rad + 6, fill=(0, 0, 0, 70))
    rr(d, cam, cx - h, cy - h, cx + h, cy + h, rad, fill=IRON)
    rr(d, cam, cx - h * .86, cy - h * .86, cx + h * .86, cy + h * .86, rad * .86, outline=IRON_D + (255,), width=9)
    rr(d, cam, cx - h * .6, cy - h * .6, cx + h * .6, cy + h * .6, rad * .6, outline=IRON_D + (255,), width=7)
    for k in range(4):                                       # cross pattern shows the rotation
        a = ang + k * math.pi / 2
        d.line([cxy(cam, cx + math.cos(a) * h * .14, cy + math.sin(a) * h * .14), cxy(cam, cx + math.cos(a) * h * .56, cy + math.sin(a) * h * .56)], fill=IRON_D + (255,), width=int(10 * cam[0] * SC))
    circ(d, cam, cx, cy, h * .14, fill=IRON_L)
    X0, Y0 = cxy(cam, cx - h * .55, cy - h * .78); X1, Y1 = cxy(cam, cx - h * .2, cy - h * .9)
    d.line((X0, Y0, X1, Y1), fill=(255, 255, 255, 60), width=int(8 * cam[0] * SC))


def road(d, cam):
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=ASPH)
    for y in range(-200, 1800, 160):                          # lane dashes move with the camera
        _, Y0 = cxy(cam, 240, y); _, Y1 = cxy(cam, 240, y + 90)
        if Y0 / SC > 300 - IY0 and Y1 / SC < 1220 - IY0:
            rr(d, cam, 228, y, 252, y + 90, 6, fill=(236, 238, 242, 200))
    for i in range(70):
        x = 100 + (i * 197) % 880; y = 300 + (i * 131) % 920
        circ(d, C0, x, y, 3 + i % 3, fill=ASPH2)


# ───────── scenes ─────────
def cam_a(t):
    k = eio((t - 1.2) / 0.9)
    return (lerp(1.0, 1.3, k) + 0.04 * min(t, 1.2) / 1.2 + 0.05 * max(0, t - 2.1), 540, 760)


def scene_a(t):
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA"); cam = cam_a(t)
    road(d, cam)
    m = eio((t - 2.25) / 0.45)
    cover(d, cam, 540, 760, 190, lerp(190, 22, m))
    if 1.9 < t < 3.6:
        for ph in (0.0, 0.5):
            p = (t * 1.1 + ph) % 1
            R = 210 + 50 * p
            rr(d, cam, 540 - R, 760 - R, 540 + R, 760 + R, lerp(R, 30, m), outline=YEL + (int(255 * (1 - p) ** 1.3),), width=5)
    if t >= 3.9:
        k = back((t - 3.9) / 0.28)
        pill(d, C0, 760, 470, "보기 좋으라고?", 44, (255, 255, 255), INK, sc=k)
        if t >= 4.9:
            badge(d, C0, 860, 590, 62, RED, "x", back((t - 4.9) / 0.25))
    return im


def hole_frame(d, cam, square):
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=ASPH)
    if square:
        rr(d, cam, 340, 560, 740, 960, 18, fill=CONC); rr(d, cam, 390, 610, 690, 910, 6, fill=HOLE_C)
    else:
        circ(d, cam, 540, 760, 200, fill=CONC); circ(d, cam, 540, 760, 150, fill=HOLE_C)


def scene_b(t):
    """Square: stand the cover up, turn it to the diagonal, it drops in."""
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA"); cam = C0
    hole_frame(d, cam, True)
    stand = eio((t - 6.6) / 0.6)
    ang = math.radians(45) * eio((t - 7.9) / 1.0)
    drop = eio((t - 9.5) / 0.7)
    if t >= 7.6:
        a = ease((t - 7.6) / 0.3) * (1 - ease((t - 11.6) / 0.3))
        dashed(d, cam, (392, 612), (688, 908), YEL + (int(255 * a),))
        pill(d, cam, 820, 470, "구멍의 대각선", 38, YEL, INK, a=a, sc=back((t - 7.6) / 0.28))
    if stand < 0.999:
        h = 175; rr(d, cam, 540 - h, 760 - h * (1 - stand) - 17 * stand, 540 + h, 760 + h * (1 - stand) + 20 * stand, lerp(22, 8, stand), fill=mix(IRON, IRON_L, stand), outline=(230, 234, 242, 255))
    else:
        sc = 1 - 0.45 * drop
        col = mix(IRON, HOLE_C, drop * 0.9)
        col = mix(IRON_L, HOLE_C, drop * 0.9)
        rbox(d, cam, 540, 760 + 30 * drop, 350 * sc, 40 * sc, ang, col + (int(255 * (1 - drop * 0.6)),), outline=(230, 234, 242, int(255 * (1 - drop))))
    if t >= 10.4:
        badge(d, cam, 820, 1060, 66, RED, "!", back((t - 10.4) / 0.25))
        pill(d, cam, 300, 1060, "쏙 빠짐", 42, RED, WHITE, sc=back((t - 10.6) / 0.28))
    return im


def scene_c(t):
    """Round: the standing cover is longer than the hole in every direction."""
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA"); cam = C0
    hole_frame(d, cam, False)
    ang = math.radians(400) * eio((t - 12.6) / 2.6)
    rbox(d, cam, 540, 760, 350, 40, ang, IRON_L + (255,), outline=(230, 234, 242, 255))
    for s in (1, -1):                                        # the ends always rest on the rim
        circ(d, cam, 540 + s * 175 * math.cos(ang), 760 + s * 175 * math.sin(ang), 15, fill=YEL + (255,))
    a = ease((t - 12.4) / 0.3)
    pill(d, cam, 540, 470, "어느 방향이든 폭이 같다", 38, YEL, INK, a=a, sc=back((t - 12.4) / 0.28))
    if t >= 15.2:
        badge(d, cam, 820, 1060, 66, GREEN, "check", back((t - 15.2) / 0.25))
        pill(d, cam, 300, 1060, "안 빠짐", 42, GREEN, INK, sc=back((t - 15.4) / 0.28))
    return im


def scene_d(t):
    """Any orientation fits: the cover spins in the air and drops into place."""
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA"); cam = C0
    road(d, cam)
    circ(d, cam, 540, 760, 200, fill=CONC); circ(d, cam, 540, 760, 178, fill=HOLE_C)
    k = eio((t - 16.8) / 1.6)
    ang = math.radians(250) * k
    cover(d, cam, 540, 760 - 60 * (1 - k), 190, 190, ang, sc=1.18 - 0.18 * k)
    if t >= 18.5:
        badge(d, cam, 840, 1080, 66, GREEN, "check", back((t - 18.5) / 0.25))
        pill(d, cam, 300, 1080, "방향 상관없음", 40, GREEN, INK, sc=back((t - 18.7) / 0.28))
    return im


def scene_e(t):
    """Side view: stood on its edge, the cover rolls like a wheel."""
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA"); cam = C0
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=(150, 196, 238))
    rr(d, C0, 70, 960, 1010, 1240, 0, fill=ASPH); rr(d, C0, 70, 1170, 1010, 1240, 70, fill=ASPH)
    u = eio((t - 20.2) / 2.6); r = 170
    cx = lerp(240, 820, u); ang = (cx - 240) / r
    circ(d, cam, cx, 960 - r, r, fill=IRON); circ(d, cam, cx, 960 - r, r * .86, outline=IRON_D + (255,), width=9)
    for k in range(6):
        a = ang + k * math.pi / 3
        d.line([cxy(cam, cx + math.cos(a) * r * .15, 960 - r + math.sin(a) * r * .15), cxy(cam, cx + math.cos(a) * r * .8, 960 - r + math.sin(a) * r * .8)], fill=IRON_D + (255,), width=int(11 * SC))
    circ(d, cam, cx, 960 - r, r * .15, fill=IRON_L)
    for i in range(3):                                       # motion streaks
        y = 960 - r + (i - 1) * 70
        dashed(d, cam, (cx - r - 60 - 120, y), (cx - r - 40, y), (255, 255, 255, int(200 * (1 - u) + 40)), wd=6, dash=30)
    pill(d, cam, 540, 470, "굴려서 이동", 44, YEL, INK, sc=back((t - 20.5) / 0.28) if t >= 20.5 else 0)
    return im


def scene_f(t):
    im = BG_ILL.copy(); d = ImageDraw.Draw(im, "RGBA")
    k = eio((t - 23.0) / 1.4); cam = (lerp(1.25, 1.0, k), 540, 760)
    road(d, cam)
    cover(d, cam, 540, 760, 190, 190, math.radians(250))
    if t > 23.5:
        for ph in (0.0, 0.5):
            p = (t * 1.1 + ph) % 1
            circ(d, cam, 540, 760, 210 + 50 * p, outline=YEL + (int(255 * (1 - p) ** 1.3),), width=5)
    return im


def illus(t):
    def scene(tt):
        if tt < 6.0: return scene_a(tt)
        if tt < 12.0: return scene_b(tt)
        if tt < 16.5: return scene_c(tt)
        if tt < 20.0: return scene_d(tt)
        if tt < 23.0: return scene_e(tt)
        return scene_f(tt)
    for cut in (6.0, 12.0, 16.5, 20.0, 23.0):
        if cut <= t < cut + 0.26:
            return Image.blend(scene(cut - 0.001), scene(t), eio((t - cut) / 0.26))
    return scene(t)


Y_, W_ = YEL, WHITE
CAPS = [
    (0.0, 1.4, None, None), (1.4, 3.6, None, None),
    (3.6, 6.0, [("보기 좋으라고?", W_)], [("아닙니다", Y_)]),
    (6.0, 9.0, [("네모 뚜껑을 세워서", W_)], [("대각선", Y_), ("으로 돌리면", W_)]),
    (9.0, 12.0, [("구멍 속으로", W_)], [("쏙 빠집니다", Y_)]),
    (12.0, 16.5, [("원은 어느 방향이든", W_)], [("폭이 같아", Y_), (" 안 빠집니다", W_)]),
    (16.5, 20.0, [("게다가 아무 방향으로", W_)], [("덮어도 딱 맞고", Y_)]),
    (20.0, 23.0, [("세워서 굴리면", W_)], [("옮기기도 쉽죠", Y_)]),
    (23.0, 25.0, [("길에서 맨홀 뚜껑을", W_)], [("찾아보세요", Y_)]),
    (25.0, 27.0, [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)]),
]


def frame(t):
    im = BG.copy()
    im.paste(illus(t).reduce(SC), (0, IY0 + SHIFT), ILL_MASK)
    im = im.convert("RGBA")
    signature2(im, t)
    if t < 1.52:
        a = min(1, t / 0.08) * (1 - ease((t - 1.36) / 0.14))
        ov = Image.new("RGBA", (W, IH), (8, 12, 28, 255)); ov.putalpha(ILL_MASK.point(lambda v: int(v * 0.49 * a)))
        im.alpha_composite(ov, (0, IY0 + SHIFT))
    kinetic(im, t, 0.0, 1.5, [[[("이거", WHITE)]], [[("알고", YEL)], [("있었나요?", YEL)]]], (690, 850), 128, stagger=0.17, slam=0.9)
    kinetic(im, t, 1.4, 3.6, [[[("맨홀", WHITE)], [("뚜껑이", WHITE)]], [[("네모", YEL), ("라면?", WHITE)]]], (1388, 1500), 84, stagger=0.14, slam=0.5)
    if t >= 25.2:
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1252, 1.0, 0.6 + 0.4 * back((t - 25.2) / 0.28))
    for t0, t1, l1, l2 in CAPS[2:]:
        if t0 <= t < t1:
            a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if t1 < DUR else 1
            for i, (segs, cy) in enumerate(((l1, 1388), (l2, 1500))):
                lt = t - t0 - i * 0.13
                if lt >= 0:
                    put(im, line_img(tuple(segs)), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
    return im.convert("RGB")


def sfx(path):
    sr = 44100; n = int(DUR * sr); x = np.zeros(n); rng = np.random.default_rng(7)
    def add(at, sig):
        i = int(at * sr); sig = sig[: max(0, n - i)]; x[i:i + len(sig)] += sig
    def env(m, dd): return np.exp(-np.arange(m) / sr / dd)
    def pop(at, f0=620, vol=.22):
        m = int(.12 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * (f0 + 380 * np.exp(-tt * 40)) * tt) * env(m, .03))
    def whoosh(at, ln=.38, vol=.2):
        m = int(ln * sr); z = rng.standard_normal(m); y = np.zeros(m); s = 0.0; a = np.linspace(.02, .35, m)
        for i in range(m):
            s += a[i] * (z[i] - s); y[i] = s
        add(at - ln * .6, vol * 3 * y * np.sin(np.pi * np.arange(m) / m) ** 2)
    def ding(at, f=1320, vol=.2, dd=.22):
        m = int(.7 * sr); tt = np.arange(m) / sr
        add(at, vol * (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.01 * tt)) * env(m, dd))
    def thud(at, vol=.5):
        m = int(.25 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-tt * 30)) / sr) * env(m, .07) + .25 * rng.standard_normal(m) * env(m, .006))
    def buzz(at, vol=.2):
        m = int(.28 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sign(np.sin(2 * np.pi * 150 * tt)) * env(m, .12) * .6)
    def clank(at, vol=.25):
        m = int(.5 * sr); tt = np.arange(m) / sr
        add(at, vol * sum(np.sin(2 * np.pi * f * tt) * g for f, g in ((620, 1), (1530, .6), (2710, .4))) * env(m, .09))
    for t0, *_ in CAPS:
        pop(t0 + .02)
    pop(.17, 760, .22); pop(.34, 920, .26); pop(1.52, 700, .18); pop(1.66, 780, .18); pop(1.80, 860, .18); whoosh(1.5, .3, .16); ding(2.3, 1568, .16)
    pop(3.9, 900, .2); buzz(4.9); thud(4.9, .35)
    whoosh(6.0); pop(7.6, 980, .2); whoosh(8.2, .5, .14)
    whoosh(9.9, .6, .2); thud(10.25, .5); clank(10.3, .2); thud(10.4, .3)
    whoosh(12.0); pop(12.4, 900, .2); whoosh(13.6, .7, .12); clank(15.2, .14); ding(15.2, 1047, .16); ding(15.34, 1568, .16)
    whoosh(16.5); clank(18.3, .3); ding(18.5, 1175, .16)
    whoosh(20.0); pop(20.5, 860, .2)
    m = int(2.6 * sr); h = np.diff(rng.standard_normal(m), prepend=0) * env(m, 2.0) * np.sin(np.pi * np.arange(m) / m); add(20.2, .05 * h)
    whoosh(23.0); ding(25.2, 1319, .16); ding(25.34, 1760, .16)
    x = np.tanh(x * 1.3) * .9
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        ims = [frame(float(v)).resize((360, 640), Image.LANCZOS) for v in sys.argv[3:]]
        s = Image.new("RGB", (360 * len(ims), 640))
        for i, im in enumerate(ims):
            s.paste(im, (i * 360, 0))
        s.save(f"{OUT}/{sys.argv[2]}.jpg", quality=88)
    else:
        music, final = sys.argv[2], sys.argv[3]
        sfx(f"{OUT}/s4_sfx.wav"); tmp = f"{OUT}/s4.part.mp4"; fo = DUR - 0.8
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-i", music, "-i", f"{OUT}/s4_sfx.wav",
                              "-filter_complex", f"[1:a]atrim=0:{DUR},volume=-9dB,afade=t=in:d=0.05,afade=t=out:st={fo}:d=0.8[m];[2:a]volume=0dB[s];[m][s]amix=inputs=2:normalize=0[a]",
                              "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, final); print("ok", final)
