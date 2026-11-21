"""45편 - 지금 콧구멍 하나는 쉬고 있어요 (비주기, nasal cycle)
사용자 요청(11/21): "맞춤법 주제가 궁금할까? 바이럴이 될 수 있는, 남한테 꼭 공유하고 싶은 주제로" →
공유 욕구 위주로 10개 재대결(아레나 2회차 상위권 + 공유형): 1등 '코는 한쪽으로만 숨 쉰다' → 사용자 선택.
사실:
- 콧속 비갑개(turbinate)가 양쪽에서 번갈아 부풀고 줄어, 한쪽이 더 막히고 다른 쪽이 열린다. 몇 시간마다 바뀜
  (Cleveland Clinic 2023-10-06 "Why Do I Sometimes Get Congested in One Nostril?" — 4~6시간마다,
  주기가 정상이면 알아채지 못함 https://health.clevelandclinic.org/why-do-i-sometimes-get-stuffy-in-one-nostril)
- 깨어 있을 때 평균 약 2시간(2.02±1.7h), 잘 때 4.5시간; 옆으로 누우면 위쪽 콧구멍 공기 흐름이 더 많다
  (Kahana-Zweig 외, PLoS ONE 2016 "Measuring and Characterizing the Human Nasal Cycle" https://pmc.ncbi.nlm.nih.gov/articles/PMC5053491)
- 왜 그런지는 아무도 확실히 모름, 유력한 설: 한쪽에 수분이 차서 너무 마르지 않게 (Live Science 2021-09-18
  https://www.livescience.com/breathing-nose-sides) · 감기 때 양쪽이 막히는 건 비주기 때문이 아님
그대로: 평면 그림 · steady 목소리 · 6초 같은 대상 안 첫 보상(H16) · 첫 장면 가운데 코 하나(H15) · 끝 = 첫 장면(H13).
바꿀 것 1개: 시청자가 보는 즉시 따라 해 보는 '참여형' 주제(지금 코를 막아 보세요) → 공유·댓글 인증 기대."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
NOSE = (255, 206, 170)
NOSE2 = (236, 172, 136)
HOLE = (120, 60, 60)
AIR = (150, 220, 255)
SWELL = (240, 110, 120)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def lw(v):
    return max(2, int(v * C0[0] * SC))


def nose(d, cx, cy, s=1.0, open_l=1.0, open_r=0.3):
    """Big front-view nose: bridge + rounded tip + two nostrils. open_* 0..1 sets nostril size."""
    P = lambda x, y: cxy(C0, cx + x * s, cy + y * s)
    d.polygon([P(-55, -250), P(55, -250), P(120, 40), P(-120, 40)], fill=NOSE + (255,))
    for (x, r) in ((-150, 95), (150, 95)):
        X0, Y0 = P(x - r, 40 - r * 0.85); X1, Y1 = P(x + r, 40 + r * 0.85)
        d.ellipse((X0, Y0, X1, Y1), fill=NOSE2 + (255,))
    X0, Y0 = P(-150, -60); X1, Y1 = P(150, 160)
    d.ellipse((X0, Y0, X1, Y1), fill=NOSE + (255,))
    for (x, o) in ((-85, open_l), (85, open_r)):
        rw, rh = 30 + 30 * o, 14 + 20 * o
        X0, Y0 = P(x - rw, 120 - rh); X1, Y1 = P(x + rw, 120 + rh)
        d.ellipse((X0, Y0, X1, Y1), fill=HOLE + (255,))


def airflow(d, x, y, t, k=1.0, n=3, s=1.0):
    if k <= 0.02:
        return
    for i in range(n):
        ph = (t * 1.2 + i / n) % 1.0
        pts = [cxy(C0, x + (i - (n - 1) / 2) * 26 * s + 10 * math.sin(j * 0.8 + t * 6), y + 40 * s + (ph * 220 + j * 12) * s) for j in range(8)]
        d.line(pts, fill=AIR + (int(230 * k * (1 - ph)),), width=lw(8 * s))


def xmark(d, x, y, R, col=RED):
    X, Y = cxy(C0, x, y); R = R * C0[0] * SC
    d.line([(X - R, Y - R), (X + R, Y + R)], fill=col + (255,), width=lw(14))
    d.line([(X - R, Y + R), (X + R, Y - R)], fill=col + (255,), width=lw(14))


def section(d, cx, cy, sl, sr, s=1.0):
    """Cross-section of the nose: two air channels, turbinate bumps that swell (sl/sr 0..1)."""
    rr(d, C0, cx - 330 * s, cy - 260 * s, cx + 330 * s, cy + 260 * s, 60 * s, fill=NOSE2 + (255,))
    for (x, sw) in ((-160, sl), (160, sr)):
        rr(d, C0, cx + (x - 110) * s, cy - 220 * s, cx + (x + 110) * s, cy + 220 * s, 40 * s, fill=(60, 40, 50, 255))
        for yy in (-120, 20, 150):
            r = (40 + 60 * sw) * s
            circ(d, C0, cx + (x - 110) * s + r * 0.4, cy + yy * s, r, fill=SWELL + (255,))
            circ(d, C0, cx + (x + 110) * s - r * 0.4, cy + yy * s, r, fill=SWELL + (255,))
    rr(d, C0, cx - 20 * s, cy - 260 * s, cx + 20 * s, cy + 260 * s, 10 * s, fill=NOSE + (255,))


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: big nose in the middle, slow zoom; left breathes, right barely; red mark on the resting side
    panel(d, BG1)
    z = 1.0 + 0.10 * ez(r / 2.6)
    nose(d, 540, 840, 1.0 * z, 1.0, 0.25)
    airflow(d, 540 - 85 * z, 840 + 120 * z, r, 1.0, s=z)
    if r > 1.6:
        emo(im, 540 + 85 * z + 90, 1080, 110 * kpop(r, 1.6, .3), "😴")
        rings(d, C0, 540 + 85 * z, 840 + 120 * z, 70, r - 1.6, col=YEL, spread=40)


def sTry(r, im, d):  # 손가락으로 한쪽씩 막고 숨 쉬어 보세요
    panel(d, (46, 40, 76))
    side = 0 if (r % 2.0) < 1.0 else 1
    nose(d, 540, 760, 0.95, 1.0, 0.25)
    fx = 540 - 230 if side == 0 else 540 + 230
    emo(im, fx, 820, 230 * kpop(r, 0.1, .3), "☝️", rot=-25 if side == 0 else 25)
    if side == 0:
        airflow(d, 540 + 85, 820, r, 0.35)
    else:
        airflow(d, 540 - 85, 820, r, 1.0)
    pill(d, C0, 540, 1150, "한쪽씩 막고 후~", 62, YEL, INK, sc=kpop(r, 0.3))


def sNotBroken(r, im, d):  # 한쪽이 더 답답하죠? 고장 난 게 아니에요
    panel(d, BG1)
    nose(d, 540, 760, 0.95, 1.0, 0.25)
    airflow(d, 455, 820, r, 1.0)
    if r > 0.3:
        pill(d, C0, 300, 400, "뻥 뚫림", 56, GREEN, INK, sc=kpop(r, 0.3))
        pill(d, C0, 780, 400, "답답", 56, RED, WHITE, sc=kpop(r, 0.6))
    if r > 1.3:
        stamp(d, C0, 540, 1150, "고장 아님!", r, 1.3, GREEN, 66)


def sSwell(r, im, d):  # 코 안쪽 살이 한쪽은 부풀고 한쪽은 줄어요
    panel(d, (40, 50, 84))
    k = ez((r - 0.3) / 1.2)
    section(d, 540, 760, 0.1, 0.1 + 0.85 * k)
    pill(d, C0, 540, 400, "코 속 단면", 54, WHITE, INK, sc=kpop(r, 0.05))
    if r > 1.2:
        pill(d, C0, 380, 1110, "줄어듦", 54, GREEN, INK, sc=kpop(r, 1.2))
        pill(d, C0, 700, 1110, "부풂", 54, RED, WHITE, sc=kpop(r, 1.5))


def sShift(r, im, d):  # 몇 시간마다 양쪽이 교대 근무
    panel(d, (52, 44, 84))
    w = 0.5 + 0.5 * math.cos(r * math.pi / 1.6)
    section(d, 540, 700, 0.95 - 0.85 * w, 0.1 + 0.85 * w, s=0.85)
    emo(im, 300, 1080, 120 * kpop(r, 0.2, .3), "🔄")
    pill(d, C0, 640, 1080, "교대 근무", 66, YEL, INK, sc=kpop(r, 0.4))


def clock(d, cx, cy, R, prog):
    circ(d, C0, cx, cy, R + 12, fill=(60, 70, 110, 255))
    circ(d, C0, cx, cy, R, fill=(246, 248, 252, 255))
    if prog > 0:
        X0, Y0 = cxy(C0, cx - R * 0.9, cy - R * 0.9); X1, Y1 = cxy(C0, cx + R * 0.9, cy + R * 0.9)
        d.pieslice((X0, Y0, X1, Y1), -90, -90 + 360 * prog, fill=BLUE + (130,))
    a = 2 * math.pi * prog
    d.line([cxy(C0, cx, cy), cxy(C0, cx + R * 0.75 * math.sin(a), cy - R * 0.75 * math.cos(a))], fill=INK + (255,), width=lw(12))
    circ(d, C0, cx, cy, 14, fill=INK + (255,))


def sTwoHours(r, im, d):  # 깨어 있을 땐 평균 두 시간쯤마다
    panel(d, BG1)
    prog = ez(r / 1.6) * 2 / 12
    clock(d, 540, 640, 230, prog)
    if r > 0.9:
        pill(d, C0, 540, 1000, "평균 약 2시간", 76, YEL, INK, sc=kpop(r, 0.9))
    if r > 1.8:
        emo(im, 820, 420, 110 * kpop(r, 1.8, .3), "👃")


def sLieDown(r, im, d):  # 옆으로 누우면 아래쪽 코가 막히고 위쪽이 뚫려요
    panel(d, (30, 36, 64))
    rr(d, C0, 160, 900, 920, 1060, 40, fill=(150, 120, 90, 255))
    rr(d, C0, 180, 760, 420, 900, 50, fill=(245, 245, 250, 255))
    emo(im, 340, 690, 210 * kpop(r, 0.05, .3), "😴", rot=90)
    rr(d, C0, 420, 800, 900, 920, 60, fill=(120, 160, 230, 255))
    if r > 0.8:
        pill(d, C0, 640, 430, "위쪽 코: 뻥", 56, GREEN, INK, sc=kpop(r, 0.8))
    if r > 1.5:
        pill(d, C0, 640, 1150, "아래쪽 코: 막힘", 56, RED, WHITE, sc=kpop(r, 1.5))


def sWhy(r, im, d):  # 쉬는 쪽을 촉촉하게 지킨다는 설
    panel(d, (40, 60, 90))
    section(d, 540, 700, 0.1, 0.9, s=0.85)
    for i in range(4):
        ph = (r * 0.8 + i / 4) % 1.0
        emo(im, 680 + 40 * math.sin(i * 2), 520 + 360 * ph, 60, "💧", a=1 - ph)
    if r > 0.6:
        pill(d, C0, 540, 1100, "쉬는 쪽은 촉촉 충전", 56, YEL, INK, sc=kpop(r, 0.6))
    if r > 1.6:
        emo(im, 830, 400, 100 * kpop(r, 1.6, .3), "🤔")


def sShare(r, im, d):  # 지금 해 보고 친구한테도
    panel(d, (46, 40, 76))
    emo(im, 380, 760, 240 * kpop(r, 0.1, .3), "🤭")
    emo(im, 700, 760, 240 * kpop(r, 0.4, .3), "😮")
    if r > 1.0:
        emo(im, 860, 450, 140 * kpop(r, 1.0, .3), "📲")
        rings(d, C0, 860, 450, 70, r - 1.0, col=YEL, spread=40)
    if r > 1.6:
        pill(d, C0, 540, 1080, "친구도 해 보게!", 60, YEL, INK, sc=kpop(r, 1.6))


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 코
    panel(d, BG1)
    nose(d, 540, 840, 1.1, 1.0, 0.25)
    airflow(d, 540 - 85 * 1.1, 840 + 120 * 1.1, r, 1.0, s=1.1)
    emo(im, 840, 420, 120 * kpop(r, 0.3, .25), "🔔")


SPOKEN = [
    "지금 콧구멍 두 개 중 하나는, 쉬고 있어요.",
    "손가락으로 한쪽씩 막고, 숨을 쉬어 보세요.",
    "한쪽이 더 답답하죠? 고장 난 게 아니에요.",
    "코 안쪽 살이, 한쪽은 부풀고 한쪽은 줄어들어요.",
    "그리고 몇 시간마다, 양쪽이 교대 근무를 해요.",
    "깨어 있을 땐, 평균 두 시간쯤마다 바뀐대요.",
    "옆으로 누우면, 아래쪽 코가 막히고 위쪽이 뚫려요.",
    "쉬는 쪽을 촉촉하게 지키려는 거라는 설이 유력해요.",
    "지금 바로 해 보고, 친구한테도 꼭 보내 보세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 10
BREATHS = (2, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("손가락으로 ", W_), ("한쪽씩", Y_), (" 막고", W_)], [("숨을 쉬어 보세요", W_)], sTry),
    ("", [("한쪽이 더 ", W_), ("답답", Y_), ("하죠?", W_)], [("고장 난 게 ", W_), ("아니에요", Y_)], sNotBroken),
    ("", [("코 안쪽 살이", W_)], [("한쪽은 ", W_), ("부풀고", Y_), (" 한쪽은 줄어요", W_)], sSwell),
    ("", [("몇 시간마다", W_)], [("양쪽이 ", W_), ("교대 근무", Y_)], sShift),
    ("", [("깨어 있을 땐", W_)], [("평균 ", W_), ("2시간", Y_), ("쯤마다", W_)], sTwoHours),
    ("", [("옆으로 누우면", W_)], [("아래쪽 ", W_), ("막힘", Y_), (", 위쪽 ", W_), ("뻥", Y_)], sLieDown),
    ("", [("쉬는 쪽을 ", W_), ("촉촉", Y_), ("하게", W_)], [("지키려는 거라는 설", W_)], sWhy),
    ("", [("지금 해 보고", W_)], [("친구한테도 ", W_), ("보내 보세요", Y_)], sShare),
    ("", [("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드려요", W_)], sEnd),
]
T = (("지금 콧구멍 하나는", W_), (" 쉬는 중", Y_))
Q = [[[("지금", W_)], [("콧구멍 하나는", W_)]], [[("쉬는 중", Y_)]]]
EV = lambda s: [("pop", s[0] + 0.05, 700), ("pop", s[0] + 0.6, 800), ("pop", s[0] + 1.6, 1100),
                ("whoosh", s[1] + 0.05), ("pop", s[1] + 0.4, 900), ("whoosh", s[1] + 2.0),
                ("pop", s[2] + 0.3, 800), ("pop", s[2] + 0.6, 900), ("thud", s[2] + 1.3, .5),
                ("pop", s[3] + 0.1, 700), ("pop", s[3] + 1.2, 800), ("pop", s[3] + 1.5, 900),
                ("whoosh", s[4] + 0.05), ("pop", s[4] + 0.4, 900),
                ("pop", s[5] + 0.9, 1000), ("pop", s[5] + 1.8, 800),
                ("pop", s[6] + 0.1, 700), ("pop", s[6] + 0.8, 900), ("thud", s[6] + 1.5, .5),
                ("pop", s[7] + 0.6, 900), ("pop", s[7] + 1.6, 800),
                ("pop", s[8] + 0.1, 800), ("pop", s[8] + 1.0, 1000), ("yes", s[8] + 1.6),
                ("pop", s[9] + 0.3, 1000)]
EP = build(45, "ep45", LINES, T, Q, EV, qsize=104, qys=(1360, 1470), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img, F, IY0, SHIFT


def _center_q(im, t):  # word-by-word pang; strongest on '쉬는 중' (H17)
    if t >= EP.qend:
        return
    out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
    rows, ys, size = EP.qhook
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size); idx = 0
    hits = [0.05, 0.4, 1.6]
    strong = [0.12, 0.12, 0.35]
    for words, cy in zip(rows, ys):
        ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) for w in words]
        sp = size * 0.34; x = 540 - (sum(ws) + sp * (len(ws) - 1)) / 2
        for w, ww in zip(words, ws):
            j = min(idx, len(hits) - 1); lt = t - hits[j]; idx += 1
            if lt >= 0:
                sc = 1 + strong[j] * (1 - ease(lt / 0.25))
                put(im, line_img(tuple(w), size), x + ww / 2, cy + EP.ptop - (IY0 + SHIFT), out * ease(lt / 0.08), sc)
            x += ww + sp


EP.center_q = _center_q
if __name__ == "__main__":
    main(EP, "e45")
