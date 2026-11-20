"""30편 - 전자레인지 안에는 6cm마다 차가운 자리가 있다 (회전 접시의 이유, 가운데를 비워라)
주제 아레나 2026-11-20 (100개 후보 → 중복 15개 탈락 → 85강 토너먼트) 우승: 과학 관점 '전자레인지 6cm 차가운 자리'.
사실:
- 가정용 전자레인지 2.45GHz, 파장 약 12cm → 안에서 멈춰 선 파동(정상파)이 생겨 센 곳·약한 곳이 약 6cm(반 파장)마다 번갈아 생김.
  접시가 도는 건 음식이 센 곳을 골고루 지나가게 하려는 것
  (ScienceABC https://www.scienceabc.com/innovation/why-do-we-need-a-turntable-in-microwaves)
- 접시를 빼고 초콜릿을 데우면 녹은 자국 간격 ≈ 6cm, ×2 = 파장, × 주파수 = 빛의 속도 약 3억 m/s
  (https://judylmohr.com/2017/02/22/measuring-the-speed-of-light/)
- 접시 한가운데는 덜 데워지는 자리 → 가운데를 비우고 도넛처럼 둘러 놓기 (GQ Korea 2026-07-26 https://www.gqkorea.co.kr/?p=390037)
  ※ '가운데는 돌아도 같은 자리'는 회전축이라 기하학적으로 참. '가장 차갑다'는 단정하지 않고 '덜 데워지기 쉬워요'로 말함.
바꿀 것 1개(플레이북 H16): 6~10초 리훅 줄에서 같은 물건 안의 첫 보상("진짜 이유는, 전자파가 멈춰 선 파도처럼…")을 주고,
바로 다음 질문(접시가 돌아도 안 움직이는 자리 하나)을 연다. 다른 시대·나라 이야기 없음.
그대로: 숫자 단정 첫 문장 + 0초 큰 '6cm'(H14), 평면 그림, 첫 장면 가운데 대상 하나(H15), 끝 장면 = 첫 장면(H13), 일정한 목소리."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
BODY = (226, 230, 238)
BODY2 = (186, 192, 206)
GLASS = (26, 30, 44)
LIGHT = (255, 214, 120)
HOT = (240, 72, 72)
COLD = (90, 169, 255)
PLATE = (240, 242, 246)
RICE = (250, 250, 244)
BOWL = (90, 150, 210)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def layer(im):
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); return L, ImageDraw.Draw(L)


def ell(d, x, y, rx, ry, **kw):
    X0, Y0 = cxy(C0, x - rx, y - ry); X1, Y1 = cxy(C0, x + rx, y + ry)
    d.ellipse((X0, Y0, X1, Y1), **kw)


def oven(im, d, cx, cy, s, r, glow=1.0, spin=True, cold=0.0):
    """Front view of a microwave: body, dark door window with lit cavity, turning plate with a rice bowl, dial panel."""
    w, h = 820 * s, 520 * s
    rr(d, C0, cx - w / 2 - 10 * s, cy - h / 2 - 10 * s, cx + w / 2 + 10 * s, cy + h / 2 + 30 * s, 40 * s, fill=BODY2 + (255,))
    rr(d, C0, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 34 * s, fill=BODY + (255,))
    wx0, wx1, wy0, wy1 = cx - w / 2 + 40 * s, cx + w / 2 - 230 * s, cy - h / 2 + 50 * s, cy + h / 2 - 50 * s
    rr(d, C0, wx0, wy0, wx1, wy1, 24 * s, fill=GLASS + (255,))
    # lit cavity
    g = tuple(int(GLASS[i] + (LIGHT[i] - GLASS[i]) * 0.55 * glow) for i in range(3))
    rr(d, C0, wx0 + 20 * s, wy0 + 20 * s, wx1 - 20 * s, wy1 - 20 * s, 16 * s, fill=g + (255,))
    pcx, pcy = (wx0 + wx1) / 2, wy1 - 70 * s
    ell(d, pcx, pcy, 200 * s, 34 * s, fill=PLATE + (255,), outline=BODY2 + (255,), width=3)
    # rice bowl slides a bit left/right as the plate turns
    bx = pcx + (60 * math.sin(r * 2.0) if spin else 0) * s
    rr(d, C0, bx - 95 * s, pcy - 120 * s, bx + 95 * s, pcy - 20 * s, 40 * s, fill=BOWL + (255,))
    ell(d, bx, pcy - 120 * s, 95 * s, 26 * s, fill=RICE + (255,))
    if cold > 0:  # patchy: one side steaming, other side frosty
        emo(im, bx - 60 * s, pcy - 190 * s, 70 * s * cold, "♨️")
        emo(im, bx + 60 * s, pcy - 175 * s, 62 * s * cold, "❄️")
    # door grid dots (the metal mesh)
    for i in range(14):
        for j in range(7):
            X, Y = wx0 + 30 * s + i * (wx1 - wx0 - 60 * s) / 13, wy0 + 30 * s + j * (wy1 - wy0 - 60 * s) / 6
            circ(d, C0, X, Y, 3 * s, fill=(0, 0, 0, 60))
    # control panel
    px = cx + w / 2 - 115 * s
    rr(d, C0, px - 80 * s, cy - h / 2 + 50 * s, px + 80 * s, cy - h / 2 + 120 * s, 12 * s, fill=(30, 40, 50, 255))
    txt(d, C0, px, cy - h / 2 + 85 * s, "0:30", max(8, int(44 * s)), (120, 255, 160))
    for k, yy in enumerate((cy - 20 * s, cy + 130 * s)):
        circ(d, C0, px, yy, 55 * s, fill=BODY2 + (255,))
        a = r * (1.6 if k == 0 else -1.0)
        X0, Y0 = px, yy
        d.line([cxy(C0, X0, Y0), cxy(C0, X0 + 45 * s * math.cos(a), Y0 + 45 * s * math.sin(a))], fill=(80, 86, 100, 255),
               width=max(2, int(10 * s * C0[0] * SC)))


def spots(d, cx, cy, cell, n, m, phase=0.0, a=255, center_cold=True):
    """Top-down hot/cold checkerboard: red blobs and blue blobs every `cell` px (= 6cm)."""
    for i in range(n):
        for j in range(m):
            hot = (i + j) % 2 == 0
            if center_cold:
                hot = not hot if ((n // 2 + m // 2) % 2 == 0) else hot
            x = cx + (i - (n - 1) / 2) * cell
            y = cy + (j - (m - 1) / 2) * cell
            col = HOT if hot else COLD
            pul = 1 + 0.08 * math.sin(phase * 5 + i + j)
            circ(d, C0, x, y, cell * 0.42 * pul, fill=col + (int(a * 0.55),))


def ruler(d, x0, x1, y, label, a=1.0):
    col = YEL + (int(255 * a),)
    d.line([cxy(C0, x0, y), cxy(C0, x1, y)], fill=col, width=max(3, int(8 * C0[0] * SC)))
    for x in (x0, x1):
        d.line([cxy(C0, x, y - 26), cxy(C0, x, y + 26)], fill=col, width=max(3, int(8 * C0[0] * SC)))
    if a > 0.3:
        pill(d, C0, (x0 + x1) / 2, y - 70, label, 56, YEL, INK, sc=a)


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: one microwave in the middle, running, slow zoom; second beat: cold spot ring on the bowl
    panel(d, BG1)
    z = 0.95 * (1.0 + 0.07 * ez(r / 0.6))
    oven(im, d, 540, 860, z, r, glow=0.8 + 0.2 * math.sin(r * 8))
    if r > 2.2:  # H5 second beat inside the long first line
        emo(im, 470, 900, 120 * kpop(r, 2.25, .3), "❄️")
        rings(d, C0, 470, 900, 60, r - 2.2, col=COLD, spread=24)
        emo(im, 300, 900, 100 * kpop(r, 2.6, .3), "🔍", rot=10)


def sPatchy(r, im, d):  # 데운 밥, 한쪽은 뜨겁고 한쪽은 차갑죠?
    panel(d, (46, 40, 76))
    cx, cy = 540, 820
    # big bowl of rice, close up
    rr(d, C0, cx - 300, cy - 40, cx + 300, cy + 240, 140, fill=BOWL + (255,))
    ell(d, cx, cy - 40, 300, 90, fill=RICE + (255,))
    for i in range(26):
        ell(d, cx - 250 + (i * 97) % 500, cy - 80 + (i * 53) % 80, 18, 9, fill=(236, 236, 226, 255))
    k = kpop(r, 0.2)
    emo(im, cx - 150, cy - 170 - 20 * math.sin(r * 4), 140 * k, "♨️")
    emo(im, cx + 150, cy - 150, 130 * kpop(r, 0.7), "❄️")
    if r > 1.1:
        pill(d, C0, cx - 150, cy + 340, "뜨거움", 52, HOT, WHITE, sc=kpop(r, 1.1))
        pill(d, C0, cx + 150, cy + 340, "차가움", 52, COLD, INK, sc=kpop(r, 1.3))
    emo(im, cx, 470, 130 * kpop(r, 1.6, .3), "🤔")


def sWave(r, im, d):  # 진짜 이유: 멈춰 선 파도 (정상파) - same oven, cut-away
    panel(d, (30, 36, 64))
    x0, x1, cy = 150, 930, 760
    rr(d, C0, x0 - 30, cy - 260, x1 + 30, cy + 260, 30, outline=BODY + (255,), width=10)
    k = ez(r / 0.4)
    L = 2 * math.pi / 260  # one half-wave = 130 px (= "6cm") so antinodes 130 px apart
    pts = []
    for i in range(121):
        x = x0 + (x1 - x0) * i / 120
        y = cy - 170 * k * math.sin(L * (x - x0)) * math.cos(r * 7)
        pts.append(cxy(C0, x, y))
    d.line(pts, fill=YEL + (255,), width=max(4, int(12 * C0[0] * SC)), joint="curve")
    if r > 0.8:
        for n in range(7):
            x = x0 + 65 + n * 130
            if x > x1:
                break
            emo(im, x, cy + 200, 70 * kpop(r, 0.8 + 0.1 * n, .25), "🔥")
        for n in range(6):
            x = x0 + 130 + n * 130
            if x < x1:
                circ(d, C0, x, cy, 16 * kpop(r, 1.0 + 0.1 * n, .25), fill=COLD + (255,))
    emo(im, 540, 360, 120 * kpop(r, 0.1, .3), "📡")


def sSpots(r, im, d):  # 센 곳과 약한 곳이 6cm 간격으로 번갈아
    panel(d, BG1)
    cell = 150
    a = int(255 * ez(r / 0.5))
    spots(d, 540, 780, cell, 5, 5, r, a)
    if r > 0.6:
        ruler(d, 540 - cell, 540, 780 - cell * 2 - 40, "6cm", ez((r - 0.6) / 0.3))
        for i, (x, y) in enumerate(((540 - cell, 780 - cell), (540, 780 - cell))):
            emo(im, x, y, 60 * kpop(r, 0.7 + 0.15 * i, .25), "🔥" if i == 0 else "❄️")


def turntable(im, d, cx, cy, R, ang, food=True, mark_center=False, ring=False):
    circ(d, C0, cx, cy, R, fill=PLATE + (235,), outline=BODY2 + (255,), width=6)
    circ(d, C0, cx, cy, R * 0.92, outline=(210, 214, 222, 255), width=3)
    if food and not ring:
        for k, ch in enumerate(("🍙", "🥟", "🍗")):
            a = ang + k * 2.1
            emo(im, cx + R * 0.58 * math.cos(a), cy + R * 0.58 * math.sin(a), 110, ch)
    if ring:
        for k in range(8):
            a = ang + k * math.pi / 4
            emo(im, cx + R * 0.66 * math.cos(a), cy + R * 0.66 * math.sin(a), 95, "🥟")
    if mark_center:
        circ(d, C0, cx, cy, 18, fill=YEL + (255,))


def sTurn(r, im, d):  # 그래서 접시가 돈다 - food passes through hot spots
    panel(d, (40, 50, 84))
    spots(d, 540, 780, 150, 5, 5, r, 200)
    ang = r * 1.4
    turntable(im, d, 540, 780, 330, ang)
    # curved arrow showing rotation
    pts = [cxy(C0, 540 + 400 * math.cos(t), 780 + 400 * math.sin(t)) for t in [ang * 0.3 + i * 0.05 for i in range(24)]]
    d.line(pts, fill=YEL + (255,), width=max(4, int(10 * C0[0] * SC)))
    emo(im, 540 + 400 * math.cos(ang * 0.3 + 1.2), 780 + 400 * math.sin(ang * 0.3 + 1.2), 70, "🔄")


def sCenterQ(r, im, d):  # 리훅: 돌아도 안 움직이는 자리 딱 하나
    panel(d, (52, 44, 84))
    ang = r * 1.4
    turntable(im, d, 540, 820, 330, ang)
    if r > 0.7:
        emo(im, 540, 820, 150 * kpop(r, 0.7, .3), "❓")
        rings(d, C0, 540, 820, 70, r - 0.7, col=YEL, spread=40)
    pill(d, C0, 540, 400, "딱 하나", 66, YEL, INK, sc=kpop(r, 0.3))


def sCenter(r, im, d):  # 바로 한가운데 - always on the same spot
    panel(d, BG1)
    spots(d, 540, 800, 150, 5, 5, r, 210)
    ang = r * 1.4
    turntable(im, d, 540, 800, 330, ang, food=False, mark_center=True)
    for k in range(3):  # edge dots move around
        a = ang + k * 2.1
        circ(d, C0, 540 + 260 * math.cos(a), 800 + 260 * math.sin(a), 22, fill=GREEN + (255,))
    emo(im, 540, 800, 110 * kpop(r, 0.2, .3), "❄️")
    if r > 0.9:
        stamp(d, C0, 540, 400, "계속 같은 자리", r, 0.9, RED, 56)


def sDonut(r, im, d):  # 가운데 비우고 도넛처럼
    panel(d, (40, 60, 90))
    ang = r * 1.0
    turntable(im, d, 540, 800, 330, ang, ring=True)
    k = kpop(r, 0.4)
    if k > 0:
        X, Y = cxy(C0, 540, 800)
        R = 80 * k * C0[0] * SC
        d.line([(X - R, Y - R), (X + R, Y + R)], fill=RED + (255,), width=max(4, int(14 * C0[0] * SC)))
        d.line([(X - R, Y + R), (X + R, Y - R)], fill=RED + (255,), width=max(4, int(14 * C0[0] * SC)))
    emo(im, 540, 380, 120 * kpop(r, 1.0, .3), "🍩")
    badge(d, C0, 880, 400, 60, GREEN, "check", kpop(r, 1.3, .25))


def sChoco(r, im, d):  # 초콜릿 녹은 자국 간격 → 빛의 속도
    panel(d, (46, 40, 76))
    x0, x1, cy = 200, 880, 720
    rr(d, C0, x0, cy - 110, x1, cy + 110, 18, fill=(110, 66, 40, 255))
    for i in range(1, 6):
        X = x0 + i * (x1 - x0) / 6
        d.line([cxy(C0, X, cy - 110), cxy(C0, X, cy + 110)], fill=(86, 50, 30, 255), width=max(2, int(5 * C0[0] * SC)))
    melt = [(x0 + 170, cy), (x0 + 170 + 300, cy)]
    for i, (x, y) in enumerate(melt):
        k = ez((r - 0.3 - 0.3 * i) / 0.5)
        circ(d, C0, x, y, 70 * k, fill=(160, 100, 60, 255))
        circ(d, C0, x - 15, y - 15, 30 * k, fill=(196, 140, 96, 255))
    if r > 1.0:
        ruler(d, melt[0][0], melt[1][0], cy + 190, "6cm", ez((r - 1.0) / 0.3))
    if r > 1.9:
        emo(im, 300, 1110, 110 * kpop(r, 1.9, .3), "💡")
        pill(d, C0, 600, 1110, "빛의 속도", 66, YEL, INK, sc=kpop(r, 2.0))
    emo(im, 540, 400, 110 * kpop(r, 0.05, .3), "🍫")


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 전자레인지
    panel(d, BG1)
    oven(im, d, 540, 860, 0.95, r, glow=0.8 + 0.2 * math.sin(r * 8))
    emo(im, 860, 470, 140 * kpop(r, 0.3, .25), "📲")
    emo(im, 220, 470, 140 * kpop(r, 1.6, .25), "👪")


SPOKEN = [
    "전자레인지 안에는, 육 센티마다 차가운 자리가 있어요.",
    "데운 밥, 한쪽만 차가웠던 적 있죠?",
    "진짜 이유는, 전자파가 멈춰 선 파도라서예요.",
    "센 곳과 약한 곳이, 육 센티마다 번갈아 생기거든요.",
    "그래서 접시가 돌아요. 음식이 센 곳을 지나가게요.",
    "그런데 돌아도 안 움직이는 자리가, 딱 하나 있어요.",
    "바로 한가운데라, 덜 데워지기 쉬워요.",
    "음식은 가운데를 비우고, 도넛처럼 놓으세요.",
    "접시 빼고 초콜릿을 데우면, 빛의 속도도 잴 수 있어요.",
    "가족에게 알려 주세요! 팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 10
BREATHS = (2, 5)
LINES = [
    ("", None, None, sHook),
    ("", [("데운 밥", W_)], [("한쪽만 ", W_), ("차가웠던 적", Y_), (" 있죠?", W_)], sPatchy),
    ("", [("진짜 이유는 전자파가", W_)], [("멈춰 선 파도", Y_), ("라서", W_)], sWave),
    ("", [("센 곳과 약한 곳이", W_)], [("6cm마다", Y_), (" 번갈아 생겨요", W_)], sSpots),
    ("", [("그래서 ", W_), ("접시가 돌아요", Y_)], [("음식이 ", W_), ("센 곳을 지나가게", Y_)], sTurn),
    ("", [("그런데 돌아도 ", W_), ("안 움직이는", Y_)], [("자리가 ", W_), ("딱 하나", Y_), (" 있어요", W_)], sCenterQ),
    ("", [("바로 ", W_), ("한가운데", Y_)], [("덜 데워지기 쉬워요", W_)], sCenter),
    ("", [("음식은 ", W_), ("가운데를 비우고", Y_)], [("도넛처럼", Y_), (" 놓으세요", W_)], sDonut),
    ("", [("접시 빼고 초콜릿을 데우면", W_)], [("빛의 속도", Y_), ("도 잴 수 있어요", W_)], sChoco),
    ("", [("가족에게 알려 주세요", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)], sEnd),
]
T = (("전자레인지", Y_), (" 6cm의 비밀", W_))
Q = [[[("전자레인지 속", W_)]]]
EV = lambda s: [("pop", s[0] + 2.25, 900),
                ("pop", s[1] + 0.2, 800), ("pop", s[1] + 0.7, 900),
                ("whoosh", s[2] + 0.05), ("pop", s[2] + 0.8, 700), ("pop", s[2] + 1.1, 800),
                ("pop", s[3] + 0.6, 900), ("thud", s[3] + 1.4, .5),
                ("whoosh", s[4] + 0.05),
                ("pop", s[5] + 0.3, 800), ("pop", s[5] + 0.7, 1000),
                ("thud", s[6] + 0.9, .5), ("pop", s[6] + 1.8, 900),
                ("pop", s[7] + 0.4, 700), ("yes", s[7] + 1.3),
                ("pop", s[8] + 1.0, 900), ("yes", s[8] + 2.0),
                ("pop", s[9] + 0.3, 1000)]
EP = build(30, "ep30", LINES, T, Q, EV, qsize=104, qys=(1420,), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img
_cq = EP.center_q


def _center_q(im, t):  # H14: the number '6cm' huge on screen from frame 0
    _cq(im, t)
    if t < EP.qend:
        out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
        put(im, line_img((("6cm", Y_),), 260), 540, 390, out, (1 + 0.12 * (1 - ease(t / 0.25))) * (1 + 0.03 * math.sin(t * 9)))


EP.center_q = _center_q
if __name__ == "__main__":
    main(EP, "e30")
