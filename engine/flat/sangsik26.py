"""1분 상식 26편 - 운동화 맨 위 남는 구멍 (볼펜 뚜껑 3편과 같은 방식: 평면 그림 + 카메라 줌 + 큰 글자, 내레이션 없음).
사실: 맨 위 여분 구멍은 힐락(heel lock)용. 같은 쪽 구멍으로 고리를 만들고 반대쪽 고리에 끼워 당기면 뒤꿈치가 신발 안에서
덜 움직여 마찰·물집이 줄어든다. 통풍용·제조 실수가 아니다 (Reader's Digest, HuffPost UK, Gear Patrol). 발 전문의가 환자들에게 권함(HuffPost UK)."""
import os, sys, math, subprocess, wave
os.environ.setdefault("SIG", "B")
import numpy as np
from PIL import Image, ImageDraw
import sangsik2 as b
from sangsik2 import *
import shoe2d as S2
LAYD = '/home/claude/work/shoe_svg'
LAY = {n: Image.open(f'{LAYD}/{n}_4x.png').convert('RGBA') for n in ('normal', 'lock', 'xray_base', 'xray_upper', 'foot', 'top')}
GEOM = {'top': (1.0, 200.0, 380.0)}
KSV, OXS, OYS = 0.92, -12.0, 592.5
PXW = 4 / KSV


def wpt(p):
    return (p[0] * KSV + OXS, p[1] * KSV + OYS)


def paste_layer(im, name, cam, rot_deg=0.0, piv=None, alpha=1.0):
    L = LAY[name]; kk, oxw, oyw = GEOM.get(name, (KSV, OXS, OYS)); f = cam[0] * SC / (4 / kk)
    ox, oy = cxy(cam, oxw, oyw); W2, H2 = im.size
    u0 = max(0, int((0 - ox) / f)); v0 = max(0, int((0 - oy) / f))
    u1 = min(L.width, int((W2 - ox) / f) + 2); v1 = min(L.height, int((H2 - oy) / f) + 2)
    if u1 <= u0 or v1 <= v0:
        return
    cr = L.crop((u0, v0, u1, v1)).resize((max(1, round((u1 - u0) * f)), max(1, round((v1 - v0) * f))), Image.BICUBIC)
    if alpha < 1:
        a = cr.getchannel('A').point(lambda v: int(v * alpha)); cr.putalpha(a)
    px, py = int(round(ox + u0 * f)), int(round(oy + v0 * f))
    if rot_deg:
        cv = Image.new('RGBA', im.size, (0, 0, 0, 0)); cv.alpha_composite(cr, (max(0, px), max(0, py)))
        cv = cv.rotate(rot_deg, resample=Image.BICUBIC, center=cxy(cam, *piv)); im.alpha_composite(cv)
    else:
        im.alpha_composite(cr, (max(0, px), max(0, py)))

DUR = 28.0
import json as _json
OB = [0, 1.4, 3.6, 6.6, 8.6, 10.0, 12.2, 15.5, 18.5, 21.5, 24.0, 26.0, 28.0]
VOD = _json.load(open("/home/claude/work/vo26f/meta.json"))
NB = [0.0]
for i in range(len(OB) - 1):
    NB.append(NB[-1] + max(OB[i + 1] - OB[i], VOD[i] + 0.38))
DUR2 = NB[-1]


def warp(tn):  # new time -> original animation time
    for i in range(len(NB) - 1):
        if tn < NB[i + 1] or i == len(NB) - 2:
            k = (tn - NB[i]) / (NB[i + 1] - NB[i]); return OB[i] + k * (OB[i + 1] - OB[i])


def unwarp(to):  # original time -> new time
    for i in range(len(OB) - 1):
        if to < OB[i + 1] or i == len(OB) - 2:
            k = (to - OB[i]) / (OB[i + 1] - OB[i]); return NB[i] + k * (NB[i + 1] - NB[i])


b.DUR = DUR
b.EP_TITLE = ((" ", WHITE),)
C0 = (1.0, 540, 760)
NAVY, NAVYL = (34, 60, 140), (70, 100, 190)
WH, WHS = (250, 250, 252), (222, 226, 236)
LACE, LACEO = (255, 255, 255), (150, 156, 172)
GUM = (196, 120, 70)
SKIN, SKIND = (255, 214, 176), (236, 178, 140)
PAPER = (246, 241, 228)
UPPER, HEEL, TOECAP, MID, OUTS = S2.UPPER, S2.HEEL, S2.TOECAP, S2.MID, S2.OUT
HOLE = (446 * 0.92 - 12.0, 314 * 0.92 + 592.5)


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


def poly(d, cam, pts, fill=None, outline=None, width=0):
    P = [cxy(cam, *p) for p in pts]
    d.polygon(P, fill=fill)
    if outline:
        d.line(P + [P[0]], fill=outline, width=int(width * SC), joint="curve")


def lline(d, cam, pts, col, w, out=None):
    P = [cxy(cam, *p) for p in pts]
    if out:
        d.line(P, fill=out, width=int((w + 7) * cam[0] * SC), joint="curve")
    d.line(P, fill=col, width=int(w * cam[0] * SC), joint="curve")


def rot(p, piv, a):
    c, s = math.cos(a), math.sin(a); x, y = p[0] - piv[0], p[1] - piv[1]
    return (piv[0] + x * c - y * s, piv[1] + x * s + y * c)


def vup(d, cam, x, y, L, col, a=1.0):
    c = col + (int(255 * a),); s = cam[0] * SC
    for sgn in (1, -1):
        X, Y0 = cxy(cam, x, y); _, Y1 = cxy(cam, x, y - sgn * L)
        d.line((X, Y0, X, Y1), fill=c, width=int(12 * s))
        d.polygon([cxy(cam, x, y - sgn * (L + 22)), cxy(cam, x - 20, y - sgn * (L - 10)), cxy(cam, x + 20, y - sgn * (L - 10))], fill=c)


# ───────── the sneaker, side view (toe to the right) ─────────
UPPER_OLD = [(232, 1018), (226, 780), (246, 712), (300, 690), (380, 694), (420, 664), (470, 650), (500, 672), (560, 742),
         (650, 818), (760, 878), (860, 916), (902, 960), (906, 1018)]
HEEL_OLD = [(232, 1018), (226, 780), (246, 712), (296, 696), (318, 760), (334, 1018)]
TOECAP_OLD = [(770, 1018), (776, 938), (820, 922), (868, 930), (900, 962), (906, 1018)]
EYES_OLD = [(482, 700), (526, 736), (570, 772), (614, 806), (658, 838), (702, 864)]


def shoe_side(im, cam, lock=0.0, ring_t=None):
    paste_layer(im, "normal", cam)
    if lock > 0:
        paste_layer(im, "lock", cam, alpha=min(1, lock))
    if ring_t is not None:
        d = ImageDraw.Draw(im, "RGBA"); X, Y = cxy(cam, *HOLE); s = cam[0] * SC
        for ph in (0.0, 0.5):
            p = (ring_t * 1.1 + ph) % 1; R = (14 + 30 * p) * s
            d.ellipse((X - R, Y - R, X + R, Y + R), outline=YEL + (int(255 * (1 - p) ** 1.3),), width=max(2, int(4 * s)))


def cam_shoe(t):
    if t < 3.6:
        k = eio((t - 1.2) / 0.9)
        return (1.0 + 0.05 * min(t, 1.2) / 1.2 + 2.0 * k + 0.15 * max(0, t - 2.1) / 1.5, lerp(540, HOLE[0], k), lerp(930, HOLE[1], k))
    if t < 6.6:
        k = eio((t - 3.6) / 0.6); return (lerp(3.2, 1.0, k), lerp(HOLE[0], 540, k), lerp(HOLE[1], 930, k))
    if t < 24.0:
        return (1.0 + 0.01 * (t - 18.5), 540, 930)
    k = eio((t - 24.0) / 1.4); return (lerp(1.055, 1.0, k), 540, 930)


def scene_shoe(t):
    im = BG_ILL.copy().convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=PAPER)
    cam = cam_shoe(t)
    lock = ease((t - 18.6) / 0.5) if t >= 18.5 else 0.0
    shoe_side(im, cam, lock, ring_t=t if (1.9 < t < 3.6 or t > 24.6) else None)
    if 3.9 <= t < 6.6:                                                          # wrong guesses
        k = back((t - 3.9) / 0.28)
        pill(d, C0, 790, 470, "통풍 구멍?", 44, (255, 255, 255), INK, sc=k)
        if t >= 4.6:
            badge(d, C0, 950, 470, 46, RED, "x", back((t - 4.6) / 0.25))
        if t >= 5.1:
            pill(d, C0, 790, 590, "그냥 장식?", 44, (255, 255, 255), INK, sc=back((t - 5.1) / 0.28))
        if t >= 5.8:
            badge(d, C0, 950, 590, 46, RED, "x", back((t - 5.8) / 0.25))
    if 18.5 <= t < 24.0:
        pill(d, C0, 760, 450, "힐락 (Heel Lock)", 50, YEL, INK, sc=back((t - 19.0) / 0.28) if t >= 19.0 else 0)
        if t >= 21.6:
            pill(d, C0, 760, 570, "물집 예방", 44, GREEN, INK, sc=back((t - 21.6) / 0.28))
            badge(d, C0, 930, 570, 44, GREEN, "check", back((t - 21.9) / 0.25))
    return im.convert("RGB")


# ───────── see-through shoe with the foot inside (cross-section style) ─────────
PIV = (860, 1004)
FOOT = [(300, 470), (392, 470), (400, 840), (430, 872), (560, 900), (700, 936), (820, 952), (868, 968), (872, 996),
        (820, 1004), (300, 1004), (272, 990), (262, 950), (276, 890), (300, 840)]
TOES = [(840, 958), (806, 950), (772, 944)]


WPIV = wpt((1030, 545))


def scene_walk(t, locked):
    im = BG_ILL.copy().convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=PAPER)
    cam = (1.0, 540, 900)
    lt = t - (6.6 if not locked else 15.5)
    ph = (lt * 1.15) % 1
    deg = 11 * math.sin(math.pi * ph) ** 2
    up = math.sin(math.pi * ph) ** 2
    rr(d, cam, 60, 1152, 1020, 1159, 4, fill=(214, 204, 184))
    sdeg = -deg if locked else 0.0
    paste_layer(im, "xray_base", cam, sdeg, WPIV)
    paste_layer(im, "foot", cam, -deg, WPIV)
    paste_layer(im, "xray_upper", cam, sdeg, WPIV)
    d = ImageDraw.Draw(im, "RGBA")
    hx, hy = wpt((214, 452))
    if not locked:
        g = 0.35 + 0.65 * up
        GLW = Image.new("RGBA", im.size, (0, 0, 0, 0)); dg = ImageDraw.Draw(GLW, "RGBA")
        for r_, a in ((54, 50), (36, 70), (20, 110)):
            circ(dg, cam, hx, hy, r_, fill=(240, 60, 40, int(a * g)))
        im.alpha_composite(GLW); d = ImageDraw.Draw(im, "RGBA")
        if up > 0.2:
            vup(d, cam, hx - 90, hy, 30 * up + 18, (235, 70, 50), a=min(1, up * 1.5))
    s = lambda k: back(k)
    if not locked:
        if lt >= 0.3:
            pill(d, C0, 700, 420, "걸을 때마다 들썩", 44, (255, 255, 255), INK, sc=s((lt - 0.3) / 0.28))
        if lt >= 2.2:
            badge(d, C0, 250, 500, 60, RED, "!", s((lt - 2.2) / 0.25))
            pill(d, C0, 700, 540, "쓸림 → 물집", 44, RED, WHITE, sc=s((lt - 2.4) / 0.28))
    else:
        if lt >= 0.4:
            pill(d, C0, 700, 420, "신발과 함께 움직임", 44, (255, 255, 255), INK, sc=s((lt - 0.4) / 0.28))
        if lt >= 1.2:
            badge(d, C0, 250, 500, 60, GREEN, "check", s((lt - 1.2) / 0.25))
            pill(d, C0, 700, 540, "뒤꿈치 꽉!", 46, GREEN, INK, sc=s((lt - 1.4) / 0.28))
    return im.convert("RGB")


# ───────── top view: how to tie it ─────────
DX = (430, 650); DROWS = [1150 - 78 * k for k in range(7)]; DTOP = [(392, 560), (688, 560)]


def loop_pts(side, bulge):
    ax, ay = DX[side], DROWS[-1]; bx, by = DTOP[side]; out = -1 if side == 0 else 1
    return [(ax + (bx - ax) * i / 12 + out * bulge * math.sin(math.pi * i / 12), ay + (by - ay) * i / 12 - 22 * math.sin(math.pi * i / 12)) for i in range(13)]


def part(pts, k):
    if k <= 0:
        return []
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; want = sum(seg) * min(1, k); out = [pts[0]]
    for i, sl in enumerate(seg):
        if want >= sl:
            out.append(pts[i + 1]); want -= sl
        else:
            f = want / sl; out.append((lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f))); break
    return out


def lace_pil(d, cam, pts, col, edge, w=18):
    if len(pts) < 2:
        return
    P = [cxy(cam, *p) for p in pts]; s = cam[0] * SC
    for c, ww in ((edge, w + 7), (col, w)):
        d.line(P, fill=c, width=int(ww * s), joint="curve")
        for q in (P[0], P[-1]):
            r = ww * s / 2; d.ellipse((q[0] - r, q[1] - r, q[0] + r, q[1] + r), fill=c)


def scene_tie(t):
    im = BG_ILL.copy().convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=PAPER)
    cam = (1.0, 540, 800)
    lt = t - 10.0
    stepA = ease((lt - 0.3) / 1.5); stepB = ease((lt - 2.2) / 1.4); pull = ease((lt - 3.7) / 0.6); bow = ease((lt - 4.4) / 0.5)
    paste_layer(im, "top", cam)
    d = ImageDraw.Draw(im, "RGBA"); s = cam[0] * SC
    if stepA <= 0.02:
        for (x, y) in DTOP:
            X, Y = cxy(cam, x, y)
            for ph in (0.0, 0.5):
                p = (t * 1.1 + ph) % 1; R = (22 + 30 * p) * s
                d.ellipse((X - R, Y - R, X + R, Y + R), outline=YEL + (int(255 * (1 - p) ** 1.3),), width=int(5 * s))
    bulge = 90 - 58 * pull
    YD = (170, 120, 0)
    for side in (0, 1):
        if stepA > 0:
            lace_pil(d, cam, part(loop_pts(side, bulge), stepA), YEL if stepB <= 0 else (255, 255, 255), YD if stepB <= 0 else (142, 151, 173))
        if stepB > 0:
            ap = loop_pts(1 - side, bulge)[6]; out = 1 if side == 0 else -1
            endp = (ap[0] + out * 26, ap[1] + 110 + 80 * pull)
            endp = (lerp(endp[0], 540 + (18 if side else -18), bow), lerp(endp[1], 655, bow))
            B = [DTOP[side], (540 + (14 if side else -14), 640), ap, endp]
            lace_pil(d, cam, part(B, stepB), YEL, YD)
    if bow > 0:
        bx, by = 540, 650
        for sgn in (-1, 1):
            loop = [(bx + sgn * 70 * bow * math.sin(math.pi * u / 2) ** 0.8 * (1 - 0.25 * math.sin(math.pi * u)), by - 46 * bow * math.sin(math.pi * u)) for u in [i / 16 for i in range(17)]]
            lace_pil(d, cam, loop, YEL, YD, 16)
            lace_pil(d, cam, [(bx, by), (bx + sgn * 30 * bow, by + 80 * bow)], YEL, YD, 16)
        circ(d, cam, bx, by, 14 * bow + 1, fill=YEL + (255,))
    if 0.05 < pull and bow < 0.3:
        for x in (250, 830):
            X, Y0 = cxy(cam, x, 760); _, Y1 = cxy(cam, x, 900); c = (235, 70, 50, 255)
            d.line((X, Y0, X, Y1), fill=c, width=int(12 * s))
            d.polygon([cxy(cam, x, 930), cxy(cam, x - 22, 892), cxy(cam, x + 22, 892)], fill=c)
    n = "①" if lt < 2.2 else "②"
    msg = "같은 쪽 맨 위 구멍에 넣어 고리" if lt < 2.2 else "반대쪽 고리에 통과 → 당기고 묶기"
    pill(d, C0, 540, 400, f"{n} {msg}", 40, YEL, INK, sc=back((lt - (0.1 if lt < 2.2 else 2.2)) / 0.28))
    return im.convert("RGB")


def illus(t):
    def scene(tt):
        if tt < 6.6: return scene_shoe(tt)
        if tt < 10.0: return scene_walk(tt, False)
        if tt < 15.5: return scene_tie(tt)
        if tt < 18.5: return scene_walk(tt, True)
        return scene_shoe(tt)
    for cut in (6.6, 10.0, 15.5, 18.5):
        if cut <= t < cut + 0.26:
            return Image.blend(scene(cut - 0.001), scene(t), eio((t - cut) / 0.26))
    return scene(t)


Y_, W_ = YEL, WHITE
CAPS = [
    (0.0, 1.4, None, None), (1.4, 3.6, None, None),
    (3.6, 6.6, [("바람 통하라고? 장식?", W_)], [("둘 다 ", W_), ("아닙니다", Y_)]),
    (6.6, 8.6, [("끈만 묶고 걸으면", W_)], [("뒤꿈치가 ", W_), ("들썩", Y_)]),
    (8.6, 10.0, [("계속 쓸리다가", W_)], [("물집", Y_), ("이 생겨요", W_)]),
    (10.0, 12.2, [("끈을 같은 쪽 맨 위 구멍에 넣어", W_)], [("작은 ", W_), ("고리", Y_), ("를 만들고", W_)]),
    (12.2, 15.5, [("엇갈려 반대쪽 고리에 통과", W_)], [("당긴 뒤 ", W_), ("평소처럼 묶기", Y_)]),
    (15.5, 18.5, [("뒤꿈치가 ", W_), ("꽉", Y_)], [("신발과 함께 움직여요", W_)]),
    (18.5, 21.5, [("이 묶는 법 이름은", W_)], [("힐락", Y_), ("(Heel Lock)", W_)]),
    (21.5, 24.0, [("발 전문가들이 권하는", W_)], [("물집 예방법", Y_)]),
    (24.0, 26.0, [("지금 운동화 맨 위", W_)], [("구멍", Y_), (" 확인해 보세요", W_)]),
    (26.0, 28.0, [("러닝하는 친구에게", W_)], [("공유", Y_), ("해 주세요", W_)]),
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
    kinetic(im, t, 1.4, 3.6, [[[("운동화", WHITE)], [("맨", WHITE)], [("위에", WHITE)]], [[("남는", WHITE)], [("구멍", YEL), ("?", WHITE)]]], (1388, 1500), 84, stagger=0.12, slam=0.5)
    if t >= 26.2:
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1252, 1.0, 0.6 + 0.4 * back((t - 26.2) / 0.28))
    for t0, t1, l1, l2 in CAPS[2:]:
        if t0 <= t < t1:
            a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if t1 < DUR else 1
            for i, (segs, cy) in enumerate(((l1, 1388), (l2, 1500))):
                lt = t - t0 - i * 0.13
                if lt >= 0:
                    put(im, line_img(tuple(segs)), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
    return im.convert("RGB")


def sfx(path):
    sr = 44100; n = int(DUR2 * sr); x = np.zeros(n); rng = np.random.default_rng(5)
    def add(at, sig):
        i = int(unwarp(min(at, DUR - 1e-3)) * sr); sig = sig[: max(0, n - i)]; x[i:i + len(sig)] += sig
    def env(m, dd): return np.exp(-np.arange(m) / sr / dd)
    def pop(at, f0=620, vol=.22):
        m = int(.12 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * (f0 + 380 * np.exp(-tt * 40)) * tt) * env(m, .03))
    def whoosh(at, ln=.38, vol=.2):
        m = int(ln * sr); z = rng.standard_normal(m); y = np.zeros(m); s = 0.0; a = np.linspace(.02, .35, m)
        for i in range(m):
            s += a[i] * (z[i] - s); y[i] = s
        add(max(0, at - ln * .6), vol * 3 * y * np.sin(np.pi * np.arange(m) / m) ** 2)
    def ding(at, f=1320, vol=.2, dd=.22):
        m = int(.7 * sr); tt = np.arange(m) / sr
        add(at, vol * (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.01 * tt)) * env(m, dd))
    def thud(at, vol=.5):
        m = int(.25 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-tt * 30)) / sr) * env(m, .07) + .25 * rng.standard_normal(m) * env(m, .006))
    def buzz(at, vol=.2):
        m = int(.28 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sign(np.sin(2 * np.pi * 150 * tt)) * env(m, .12) * .6)
    def step(at, vol=.18):
        m = int(.09 * sr); add(at, vol * rng.standard_normal(m) * env(m, .02))
    for t0, *_ in CAPS:
        pop(t0 + .02)
    pop(.17, 760, .22); pop(.34, 920, .26); pop(1.52, 700, .18); pop(1.64, 780, .18); pop(1.76, 860, .18); whoosh(1.5, .3, .16); ding(2.0, 1568, .16)
    pop(3.9, 900, .2); buzz(4.6); pop(5.1, 900, .2); buzz(5.8); thud(5.8, .3)
    whoosh(6.6)
    for k in range(4):
        step(6.6 + 0.43 + k / 1.15, .2)
    pop(6.9, 820, .2); thud(8.8, .45); ding(8.8, 440, .18, .15)
    whoosh(10.0); pop(10.2, 900, .2); ding(11.8, 1175, .14); whoosh(12.2); pop(12.3, 900, .2); thud(13.8, .35); ding(14.6, 1568, .16)
    whoosh(15.5)
    for k in range(3):
        step(15.5 + 0.43 + k / 1.15, .2)
    ding(16.7, 1047, .16); ding(16.84, 1568, .16)
    whoosh(18.5); pop(19.0, 980, .22); pop(21.6, 900, .2); ding(21.9, 1319, .16)
    whoosh(24.0); ding(26.2, 1319, .16); ding(26.34, 1760, .16)
    x *= 0.55
    import soundfile as _sf
    for i in range(len(VOD)):
        v, vsr = _sf.read(f"/home/claude/work/vo26f/l{i:02d}.wav")
        if v.ndim > 1: v = v.mean(1)
        if vsr != sr:
            v = np.interp(np.arange(int(len(v) * sr / vsr)) * vsr / sr, np.arange(len(v)), v)
        st = int((NB[i] + 0.12) * sr); v = v[: max(0, n - st)]; x[st:st + len(v)] += 0.95 * v / max(1e-6, np.abs(v).max())
    x = np.tanh(x * 1.1) * .95
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
        sfx(f"{OUT}/s26_sfx.wav"); tmp = final.replace(".mp4", ".part.mp4"); fo = DUR2 - 0.8
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-stream_loop", "-1", "-i", music, "-i", f"{OUT}/s26_sfx.wav",
                              "-filter_complex", f"[1:a]atrim=0:{DUR2},volume=-17dB,afade=t=in:d=0.05,afade=t=out:st={fo}:d=0.8[m];[2:a]volume=0dB[s];[m][s]amix=inputs=2:normalize=0[a]",
                              "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-t", str(DUR2), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR2 * FPS)):
            p.stdin.write(frame(warp(i / FPS)).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, final); print("ok", final)
