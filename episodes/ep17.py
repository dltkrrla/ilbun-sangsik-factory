"""17편 - 녹차와 말차, 뭐가 다를까"""
from kit import *
from vtl import build, main
import ep06 as o
from ep16 import sun, ray

TEA_L = (196, 206, 110)      # steeped green tea (yellow-green, clear)
MATCHA = (96, 168, 60)       # whisked matcha (vivid)
LEAF_L, LEAF_D = (150, 200, 90), (40, 120, 50)
CUP = (238, 236, 228)


def cup(d, x, y, s, liquid, foam=False, a=255, label=None, lab_bg=WHITE):
    """Tea bowl, bottom centre at (x, y)."""
    w, h = 150 * s, 120 * s
    d.polygon([cxy(C0, x - w, y - h), cxy(C0, x + w, y - h), cxy(C0, x + w * .72, y), cxy(C0, x - w * .72, y)], fill=CUP + (a,))
    rr(d, C0, x - w * .4, y - 6, x + w * .4, y + 16 * s, 6, fill=(214, 210, 200, a))
    x0, y0 = cxy(C0, x - w, y - h - 26 * s); x1, y1 = cxy(C0, x + w, y - h + 26 * s)
    d.ellipse([x0, y0, x1, y1], fill=(210, 206, 196, a))
    x0, y0 = cxy(C0, x - w * .9, y - h - 20 * s); x1, y1 = cxy(C0, x + w * .9, y - h + 20 * s)
    d.ellipse([x0, y0, x1, y1], fill=liquid + (a,))
    if foam:
        for i in range(14):
            fx = x + math.cos(i * 2.4) * w * .6 * ((i % 5) / 5 + .2); fy = y - h + math.sin(i * 2.4) * 10 * s
            circ(d, C0, fx, fy, 7 * s, fill=(150, 210, 100, a))
    if label:
        pill(d, C0, x, y + 80 * s, label, int(54 * s / 1.2), lab_bg, INK, a=a / 255)


def leaf(d, x, y, s, col, rot=0.0):
    pts = []
    for k in range(0, 41):
        u = k / 40 * 2 * math.pi
        px, py = math.cos(u) * 60 * s, math.sin(u) * 26 * s * (1 - 0.3 * math.cos(u))
        c, sn = math.cos(rot), math.sin(rot)
        pts.append(cxy(C0, x + px * c - py * sn, y + px * sn + py * c))
    d.polygon(pts, fill=col + (255,))
    c, sn = math.cos(rot), math.sin(rot)
    d.line([cxy(C0, x - 60 * s * c, y - 60 * s * sn), cxy(C0, x + 60 * s * c, y + 60 * s * sn)], fill=(255, 255, 255, 110), width=4)


def bush(d, x, y, s, col):
    for i, (dx, dy, r) in enumerate(((-90, -40, 80), (0, -90, 95), (90, -40, 80), (-45, 0, 75), (45, 0, 75))):
        circ(d, C0, x + dx * s, y + dy * s, r * s, fill=col + (255,))
    rr(d, C0, x - 12 * s, y + 40 * s, x + 12 * s, y + 120 * s, 4, fill=(110, 80, 50, 255))


def ground(d):
    rr(d, C0, 70, 1080, 1010, 1240, 0, fill=(96, 74, 52))


# ---------------- scenes ----------------
def sHook(r, im, d):
    panel(d, (38, 60, 52)); o.table(d)
    z = 1 + 0.03 * r
    cup(d, 330, 1010, 1.25 * z, TEA_L)
    cup(d, 750, 1010, 1.25 * z, MATCHA, foam=True)
    rings(d, C0, 540, 800, 170, r)


def sSame(r, im, d):
    panel(d, (40, 70, 58)); ground(d)
    bush(d, 540, 900, 1.5 * kpop(r, 0, .3) + .001, LEAF_D)
    pill(d, C0, 540, 430, "같은 차나무", 70, YEL, INK, sc=kpop(r, 0.4))
    if r > 0.9:
        k = ease((r - 0.9) / 0.4)
        cup(d, 220, 1160, 0.75 * k + .001, TEA_L); cup(d, 860, 1160, 0.75 * k + .001, MATCHA, foam=True)


def sShadeQ(r, im, d):
    panel(d, (40, 70, 58)); ground(d)
    for x in (300, 780):
        bush(d, x, 960, 1.05, LEAF_L)
    sun(im, d, 540, 470, 66, r)
    pill(d, C0, 540, 700, "차이는 ‘그늘’", 72, WHITE, INK, sc=kpop(r, 0.4))


def sShade(r, im, d):
    panel(d, (40, 70, 58)); ground(d)
    k = ease(r / 0.8)
    sun(im, d, 860, 400, 60, r)
    bush(d, 540, 990, 1.35, mix(LEAF_L, LEAF_D, ease((r - 0.9) / 1.2)))
    # shade cloth comes down
    top = lerp(300, 640, k)
    rr(d, C0, 140, top, 940, top + 40, 6, fill=(30, 30, 34, 245))
    for x in range(150, 940, 34):
        d.line([cxy(C0, x, top), cxy(C0, x, top + 40)], fill=(70, 70, 76, 255), width=3)
    for x in (160, 920):
        d.line([cxy(C0, x, top + 20), cxy(C0, x, 1080)], fill=(120, 110, 100, 255), width=8)
    for i, tx in enumerate((620, 720)):
        ray(d, (820, 450), (tx, top - 4), ease((r - 0.2 - .1 * i) / .5))
    pill(d, C0, 540, 1140, "수확 2~4주 전 ‘차광재배’", 50, YEL, INK, sc=kpop(r, 0.5))


def sColor(r, im, d):
    panel(d, (36, 56, 50))
    leaf(d, 300, 680, 2.6, LEAF_L, -0.4)
    leaf(d, 780, 680, 3.0 * (0.6 + 0.4 * kpop(r, 0.1, .3)), LEAF_D, 0.4)
    txt(d, C0, 300, 880, "햇빛", 50, WHITE)
    txt(d, C0, 780, 880, "그늘", 50, WHITE)
    txt(d, C0, 540, 680, "→", 80, WHITE)
    if r > 1.0:
        pill(d, C0, 540, 1040, "진한 초록 + 감칠맛", 60, GREEN, INK, sc=kpop(r, 1.0))


def sSteep(r, im, d):
    panel(d, (44, 52, 80)); o.table(d)
    cup(d, 420, 1040, 1.4, TEA_L)
    k = ease((r - 0.5) / 0.7)
    for i in range(4):
        leaf(d, lerp(380 + i * 30, 820, k), lerp(840 - i * 10, 760 - i * 40, k) - 120 * math.sin(k * math.pi), 0.6, LEAF_D, i + r * 3 * (k > 0))
    if k > 0.6:
        emo(im, 820, 900, 150 * kpop(r, 0.9, .25), "🗑️")
    pill(d, C0, 420, 470, "녹차 = 우린 물만", 58, WHITE, INK, sc=kpop(r, 0.2))


def sMill(r, im, d):
    panel(d, (44, 52, 80)); o.table(d)
    # stone mill
    for i, (y0, h) in enumerate(((640, 90), (735, 90))):
        rr(d, C0, 330, y0, 750, y0 + h, 30, fill=(150, 150, 156, 255) if i == 0 else (128, 128, 134, 255))
    ang = r * 2.4
    hx = 540 + math.cos(ang) * 170
    rr(d, C0, hx - 14, 560, hx + 14, 690, 6, fill=(120, 84, 50, 255))
    for i in range(10):  # powder falling
        ph = (r * 1.4 + i / 10) % 1
        circ(d, C0, 540 + math.sin(i * 7) * 120, 830 + ph * 140, 7, fill=MATCHA + (int(255 * (1 - ph)),))
    cup(d, 540, 1060, 1.1, MATCHA, foam=True)
    leaf(d, 540, 520, 0.9 * kpop(r, 0, .3), LEAF_D, 0.3)
    pill(d, C0, 540, 420, "말차 = 잎을 통째로", 58, YEL, INK, sc=kpop(r, 0.3))


def sCaffeine(r, im, d):
    panel(d, (40, 52, 84))
    base = 1100
    for x, val, col, lab in ((350, 30, TEA_L, "녹차"), (730, 65, MATCHA, "말차")):
        k = ease((r - 0.2) / 0.7)
        h = val * 8 * k
        rr(d, C0, x - 90, base - h, x + 90, base, 12, fill=col + (255,))
        txt(d, C0, x, base + 70, lab, 56, WHITE)
        if k > 0.95:
            txt(d, C0, x, base - h - 60, f"약 {val}mg", 52, WHITE)
    if r > 1.1:
        put_txt = "한 잔 카페인 약 2배"
        pill(d, C0, 540, 420, put_txt, 64, YEL, INK, sc=kpop(r, 1.1))


def sEnd(r, im, d):
    panel(d, (38, 60, 52)); o.table(d)
    cup(d, 330, 1010, 1.25, TEA_L, label="녹차")
    cup(d, 750, 1010, 1.25, MATCHA, foam=True, label="말차", lab_bg=YEL)
    rings(d, C0, 750, 860, 150, r)


LINES = [
    ("녹차랑 말차, 같은 거 아니었어요?", None, None, sHook),
    ("사실 둘 다, 같은 차나무 잎이에요.", [("놀라지 마세요, 둘 다", W_)], [("같은 차나무 잎", Y_)], sSame),
    ("차이는 바로, 그늘이에요.", [("차이는 바로", W_)], [("그늘", Y_)], sShadeQ),
    ("말차는 따기 몇 주 전부터 햇빛을 가려서 키워요.", [("따기 몇 주 전부터", W_)], [("햇빛을 가려서", Y_), (" 키워요", W_)], sShade),
    ("그러면 잎이 더 진한 초록이 되고, 감칠맛이 올라가요.", [("잎이 더 진한 초록", W_)], [("감칠맛", Y_), ("이 올라가요", W_)], sColor),
    ("그리고 녹차는 잎을 우려낸 물만 마시지만,", [("녹차는", W_)], [("우려낸 물만", Y_), (" 마시고", W_)], sSteep),
    ("말차는 잎을 맷돌에 갈아서 통째로 마셔요.", [("말차는 잎을 갈아서", W_)], [("통째로", Y_), (" 마셔요", W_)], sMill),
    ("그래서 카페인도 말차가 두 배쯤 많아요.", [("카페인도 말차가 2배쯤", W_)], [("밤엔 조심!", Y_)], sCaffeine),
    ("알고 있었다면, 댓글로 알려 주세요!", [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)], sEnd),
]
T = (("녹차와 ", W_), ("말차", Y_), ("의 차이", W_))
Q = [[[("녹차랑", W_)], [("말차", Y_)]], [[("같은", W_)], [("거?", Y_)]]]
EV = lambda s: [("pop", s[1] + .4, 800), ("ding", s[2] + .4, 1175), ("whoosh", s[3] + .1), ("pop", s[3] + .5, 900),
                ("ding", s[4] + 1.0, 1568), ("whoosh", s[5] + .5), ("clank", s[5] + .95, .15), ("pop", s[6] + .3, 900),
                ("pop", s[7] + .3, 700), ("yes", s[7] + 1.1)]
EP = build(17, "ep17", LINES, T, Q, EV)
if __name__ == "__main__":
    main(EP, "e17")
