"""18편 - 흰머리는 왜 생길까? 다시 검게 될 수 있을까?"""
from kit import *
from vtl import build, main

SKIN = (236, 190, 160)
DERM = (214, 150, 130)
BLACK_H = (34, 30, 30)
WHITE_H = (238, 238, 232)
CELL = (170, 110, 220)
BULGE_Y = 690


def lerpc(a, b_, k):
    return tuple(int(a[i] + (b_[i] - a[i]) * k) for i in range(3))


def strand(d, x, y0, y1, col, w=16, wave=0.0, t=0.0):
    """Hair from root y0 up to tip y1."""
    n = 24; pts = []
    for i in range(n + 1):
        u = i / n; y = y0 + (y1 - y0) * u
        pts.append(cxy(C0, x + wave * math.sin(u * 5 + t) * u, y))
    d.line(pts, fill=col + (255,), width=w, joint="curve")


def strand2(d, x, y0, y1, c_root, c_tip, split, w=16):
    """Two-tone hair: root colour up to fraction `split`, tip colour beyond."""
    ym = y0 + (y1 - y0) * split
    d.line([cxy(C0, x, y0), cxy(C0, x, ym)], fill=c_root + (255,), width=w)
    d.line([cxy(C0, x, ym), cxy(C0, x, y1)], fill=c_tip + (255,), width=w)


def follicle(d, hair_col, grow=1.0):
    rr(d, C0, 70, 520, 1010, 600, 0, fill=SKIN + (255,))
    rr(d, C0, 70, 600, 1010, 1240, 0, fill=DERM + (255,))
    # follicle tube + bulb
    rr(d, C0, 470, 560, 610, 1010, 50, fill=(196, 128, 112, 255))
    circ(d, C0, 540, 1010, 95, fill=(188, 116, 102, 255))
    circ(d, C0, 540, 1030, 45, fill=(150, 80, 80, 255))  # papilla
    # bulge on the side
    circ(d, C0, 630, BULGE_Y, 52, fill=(204, 140, 124, 255))
    txt(d, C0, 820, BULGE_Y, "줄기세포 자리", 46, WHITE)
    # hair shaft
    top = lerp(1000, 320, grow)
    d.line([cxy(C0, 540, 1000), cxy(C0, 540, top)], fill=hair_col + (255,), width=26)


# ---------------- scenes ----------------
def sHook(r, im, d):
    panel(d, (46, 54, 86))
    emo(im, 540, 760, 400 + 12 * math.sin(r * 2), "👴")
    rings(d, C0, 540, 650, 210, r)


def sRoot(r, im, d):
    panel(d, (46, 54, 86))
    follicle(d, BLACK_H, ease((r - 0.3) / 1.6))
    k = ease((r - 0.2) / 1.0)
    x, y = lerp(630, 560, k), lerp(BULGE_Y, 990, k)
    circ(d, C0, x, y, 26, fill=CELL + (255,), outline=(255, 255, 255, 255), width=4)
    pill(d, C0, 300, 400, "색소 줄기세포", 54, YEL, INK, sc=kpop(r, 0.4))
    if k >= 1:
        for i in range(6):
            ph = (r * 1.2 + i / 6) % 1
            circ(d, C0, 540 + math.sin(i * 5) * 40, 990 - ph * 300, 9, fill=(60, 40, 30, int(255 * (1 - ph))))


def sStuck(r, im, d):
    panel(d, (46, 54, 86))
    follicle(d, WHITE_H, 0.0)
    sh = 6 * math.sin(r * 30) * (r > 0.4)
    circ(d, C0, 630 + sh, BULGE_Y, 26, fill=CELL + (255,), outline=(255, 255, 255, 255), width=4)
    emo(im, 700, 610, 90 * kpop(r, 0.6, .25), "🔒")
    pill(d, C0, 300, 400, "꽉 끼어서 못 내려감", 50, RED, WHITE, sc=kpop(r, 0.8))
    badge(d, C0, 640, 880, 50, RED, "x", kpop(r, 1.4, .25))


def sWhite(r, im, d):
    panel(d, (46, 54, 86))
    follicle(d, WHITE_H, ease(r / 1.6))
    circ(d, C0, 630, BULGE_Y, 26, fill=CELL + (255,), outline=(255, 255, 255, 255), width=4)
    pill(d, C0, 300, 400, "색 없이 자라요", 54, WHITE, INK, sc=kpop(r, 0.5))


def sQ(r, im, d):
    panel(d, (52, 44, 80))
    for i, x in enumerate((380, 480, 580, 680)):
        strand(d, x, 1150, 520, WHITE_H, w=20, wave=26, t=r * 2 + i)
    emo(im, 540, 430, 170 * kpop(r, 0.0, .3), "❓")
    k = kpop(r, 0.8)
    if k > 0:
        pill(d, C0, 540, 1180, "다시 검게?", 64, YEL, INK, sc=k)


def sStress(r, im, d):
    panel(d, (44, 62, 70))
    k = ease((r - 0.3) / 1.4)
    emo(im, 300, 560, 200, "😫" if k < 0.5 else "😌")
    # stress meter
    rr(d, C0, 200, 760, 400, 800, 18, fill=(255, 255, 255, 60))
    rr(d, C0, 200, 760, 200 + 200 * (1 - 0.8 * k), 800, 18, fill=lerpc(RED, GREEN, k) + (255,))
    txt(d, C0, 300, 850, "스트레스", 40, WHITE)
    # hair recolours from the root
    strand2(d, 740, 1180, 400, BLACK_H, WHITE_H, ease((r - 0.6) / 1.6) * 0.7, w=30)
    rr(d, C0, 600, 1180, 880, 1220, 0, fill=SKIN + (255,))
    if r > 1.2:
        pill(d, C0, 740, 340, "뿌리부터 다시 검게", 44, YEL, INK, sc=kpop(r, 1.2))


def sVacation(r, im, d):
    panel(d, (40, 86, 110))
    emo(im, 270, 520, 210 * kpop(r, 0, .3), "🏖️")
    for i in range(5):
        x = 520 + i * 100
        k = ease((r - 0.5 - i * 0.18) / 0.4)
        strand(d, x, 1170, 560, lerpc(WHITE_H, BLACK_H, k), w=22, wave=18, t=i)
    rr(d, C0, 470, 1170, 990, 1210, 0, fill=SKIN + (255,))
    if r > 1.6:
        pill(d, C0, 720, 470, "5가닥 동시에!", 56, YEL, INK, sc=kpop(r, 1.6))
    txt(d, C0, 270, 760, "2021 컬럼비아대 연구", 40, (220, 230, 240))


def sNoCure(r, im, d):
    panel(d, (52, 52, 70))
    emo(im, 540, 720, 260, "💊", rot=-12)
    badge(d, C0, 700, 600, 70, RED, "x", kpop(r, 0.5, .25))
    pill(d, C0, 540, 1000, "되돌리는 약은 아직 없음", 52, WHITE, INK, sc=kpop(r, 0.9))


def sB12(r, im, d):
    panel(d, (40, 60, 90))
    emo(im, 330, 680, 220 * kpop(r, 0, .3), "🧪")
    emo(im, 740, 680, 200 * kpop(r, 0.3, .3), "🩺")
    pill(d, C0, 540, 420, "20대에 흰머리 급증?", 54, YEL, INK, sc=kpop(r, 0.2))
    if r > 1.0:
        pill(d, C0, 540, 960, "비타민 B12 · 갑상선 검사", 48, WHITE, INK, sc=kpop(r, 1.0))


def sEnd(r, im, d):
    panel(d, (46, 54, 86))
    emo(im, 330, 740, 280, "👴")
    emo(im, 750, 740, 280, "👨")
    txt(d, C0, 540, 740, "→", 90, YEL)
    rings(d, C0, 750, 740, 160, r)


LINES = [
    ("", None, None, sHook),
    ("", [("머리카락 뿌리엔", W_)], [("색소 줄기세포", Y_), ("가 있어요", W_)], sRoot),
    ("", [("나이가 들면 이 세포가", W_)], [("꽉 끼어서", Y_), (" 못 움직여요", W_)], sStuck),
    ("", [("색을 못 만들어서", W_)], [("하얀 머리카락", Y_), ("이 나와요", W_)], sWhite),
    ("", [("다시 검게 될 수 있냐고요?", W_)], [("그런 사례가 있어요!", Y_)], sQ),
    ("", [("스트레스가 줄자", W_)], [("다시 검게", Y_), (" 돌아왔어요", W_)], sStress),
    ("", [("휴가 간 사람의", W_)], [("머리카락 5가닥", Y_), ("이 검게!", W_)], sVacation),
    ("", [("오래된 흰머리를 되돌리는", W_)], [("약은 아직 없어요", Y_)], sNoCure),
    ("", [("20대에 확 늘면", W_)], [("비타민 B12 검사", Y_)], sB12),
    ("", [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)], sEnd),
]
T = (("흰머리", Y_), ("는 왜 생길까?", W_))
Q = [[[("흰머리는", W_)]], [[("왜", W_)], [("생길까?", Y_)]]]
EV = lambda s: [("pop", s[1] + .4, 800), ("buzz", s[2] + .5), ("no", s[2] + 1.4), ("whoosh", s[3] + .1), ("pop", s[4] + .8, 900),
                ("ding", s[5] + 1.2, 1568), ("pop", s[6] + 1.6, 900), ("yes", s[6] + 1.2), ("no", s[7] + .5), ("pop", s[8] + 1.0, 800)]
SPOKEN = ["여러분, 흰머리는 대체 왜 생기는 걸까요?",
          "머리카락 뿌리에는요, 색을 칠해 주는 색소 줄기세포가 있어요.",
          "그런데 나이가 들면, 이 세포가 한자리에 꽉 끼어서 움직이질 못해요.",
          "그러면 색을 못 만들고, 하얀 머리카락이 나오는 거죠.",
          "그럼 다시 검게 돌릴 수 있냐고요? 놀랍게도, 그런 사례가 있어요!",
          "스트레스가 줄었더니, 흰머리 일부가 다시 검게 돌아온 거예요.",
          "휴가 간 사람의 머리카락 다섯 가닥이, 동시에 검게 변했대요!",
          "하지만 오래된 흰머리까지 되돌리는 약은, 아직 없어요.",
          "다만 이십 대에 흰머리가 확 늘면, 비타민 비 십이 검사를 받아 보세요.",
          "알고 있었다면, 댓글로 알려 주세요!"]
EMOTIONS = ["curious", "explain", "sad", "explain", "surprised", "amazed", "excited", "secret", "explain", "bright"]
BREATHS = (2, 5, 7)
EP = build(18, "ep18", LINES, T, Q, EV, spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e18")
