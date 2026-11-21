"""43편 - 핫팩, 뜨겁지 않아도 화상 입어요 (저온화상: 40도대에서도, 아프지 않아서 더 위험)
주제 아레나 2026-11-21 (100개 후보 → 중복 21개 탈락 → 79강 토너먼트) 우승: 몸 관점 '핫팩 40도대 저온화상' (20점 만점).
사실:
- 몸은 체온보다 조금 높은 40~50도의 열에 오래 닿으면 화상을 입기 쉽다. 핫팩은 최고 70도까지, 평균 40~70도를 오래 유지.
  맨살에 쓰지 말고 수시로 부위를 옮길 것. 당뇨·수면제 복용 시 더 주의 (소방청, 정책브리핑 2021-12-13
  https://www.korea.kr/news/policyNewsView.do?newsId=148896730)
- 최고 70도 핫팩이 2시간 계속 피부에 닿으면 저온화상. 옷 위에 사용 (정책브리핑 2020-12-17, 자료 질병관리청
  https://www.korea.kr/news/healthView.do?newsId=148881289)
- 통증이 뚜렷하지 않아 알아차리기 어려움 · 옷 위라도 같은 부위에 오래 두면 손상 · 붙인 채 잠들지 말 것 · 고령자는 피부 감각이 둔함,
  한국소비자원: 옷·장갑·양말 위에 사용 (위키트리 2026-11-07 https://www.wikitree.co.kr/articles/1172673)
- 잠들기 전 이불 속에 넣어 둔 핫팩도 위험 (NHS 안내 인용, 위키트리 2026-11-10 https://www.wikitree.co.kr/articles/1173504)
바꿀 것 1개(플레이북 다음 영상 방향 1): 첫 문장에 구체적 숫자 하나("사십 도") + 0초 큰 '40℃'(H14), 강조 단어 = 숫자.
그대로: 손해형 첫 문장 · 공유형 주제 · 6초 같은 물건 안의 첫 보상("진짜 무서운 건 아프지 않다는 것", H16) ·
첫 장면 가운데 핫팩 하나(H15) · 끝 장면 = 첫 장면(H13) · steady 목소리 · 마지막 "부모님께 보내 드리세요"(L10).
※ 마스코트(AI 영상) 장면은 Higgsfield 크레딧 + 사용자 승인이 필요해 이 자동 작업에서는 평면 그림으로만 만든다."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
PACK = (246, 244, 238)
PACK2 = (214, 210, 200)
HOT = (240, 72, 72)
WARM = (255, 160, 70)
SKIN1 = (255, 214, 186)
SKIN2 = (240, 170, 150)
SKIN3 = (250, 226, 160)
COLD = (90, 169, 255)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def lw(v):
    return max(2, int(v * C0[0] * SC))


def heat_waves(d, cx, top, t, n=3, col=WARM, a=1.0, h=150, gap=70):
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * gap
        pts = []
        for k in range(20):
            y = top - k * h / 19
            pts.append(cxy(C0, x + 14 * math.sin(k * 0.7 - t * 8 + i), y))
        d.line(pts, fill=col + (int(220 * a),), width=lw(9), joint="curve")


def hotpack(im, d, cx, cy, s=1.0, t=0.0, rot_glow=1.0, label=True):
    """A disposable hand warmer: soft white pouch with a stitched edge, iron powder lumps and an orange heat band."""
    w, h = 300 * s, 400 * s
    rr(d, C0, cx - w / 2 + 12 * s, cy - h / 2 + 16 * s, cx + w / 2 + 12 * s, cy + h / 2 + 16 * s, 46 * s, fill=(0, 0, 0, 70))
    rr(d, C0, cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, 46 * s, fill=PACK2 + (255,))
    rr(d, C0, cx - w / 2 + 14 * s, cy - h / 2 + 14 * s, cx + w / 2 - 14 * s, cy + h / 2 - 14 * s, 36 * s, fill=PACK + (255,))
    for i in range(16):  # stitch dots along the edge
        u = i / 16
        for (x, y) in ((cx - w / 2 + 7 * s + (w - 14 * s) * u, cy - h / 2 + 7 * s), (cx - w / 2 + 7 * s + (w - 14 * s) * u, cy + h / 2 - 7 * s)):
            circ(d, C0, x, y, 3 * s, fill=PACK2 + (255,))
    for j in range(9):  # lumpy powder inside
        x = cx + ((j * 71) % 200 - 100) * s
        y = cy + ((j * 113) % 240 - 100) * s
        circ(d, C0, x, y, 26 * s, fill=(232, 228, 220, 255))
    g = 0.5 + 0.5 * math.sin(t * 6)
    band = tuple(int(WARM[i] * (0.85 + 0.15 * g)) for i in range(3))
    rr(d, C0, cx - w / 2 + 30 * s, cy - 40 * s, cx + w / 2 - 30 * s, cy + 40 * s, 20 * s, fill=band + (255,))
    if label:
        txt(d, C0, cx, cy, "HOT", max(8, int(60 * s)), WHITE)
    heat_waves(d, cx, cy - h / 2 - 20 * s, t, a=rot_glow, h=130 * s, gap=70 * s)


def thermo(d, x, y0, y1, val, vmax=80, label=True):
    """Vertical thermometer from y0 (top) to y1 (bulb); val in °C."""
    rr(d, C0, x - 34, y0 - 20, x + 34, y1, 34, fill=(236, 240, 246, 255))
    circ(d, C0, x, y1 + 20, 62, fill=(236, 240, 246, 255))
    circ(d, C0, x, y1 + 20, 46, fill=HOT + (255,))
    top = y1 - (y1 - y0) * min(1.0, val / vmax)
    rr(d, C0, x - 16, top, x + 16, y1 + 10, 16, fill=HOT + (255,))
    for v in range(0, vmax + 1, 10):
        yy = y1 - (y1 - y0) * v / vmax
        d.line([cxy(C0, x + 40, yy), cxy(C0, x + 64, yy)], fill=(200, 206, 220, 255), width=lw(4))


def skin(d, x0, x1, y, t, heat=0.0, depth=0.0):
    """Skin cross-section: 표피 / 진피 / 피하지방. heat 0..1 reddens; depth 0..1 = how deep the damage reaches."""
    layers = [(SKIN1, 70), (SKIN2, 130), (SKIN3, 150)]
    yy = y
    for k, (col, hh) in enumerate(layers):
        rr(d, C0, x0, yy, x1, yy + hh, 18 if k in (0, 2) else 0, fill=col + (255,))
        yy += hh
    if heat > 0:
        cx = (x0 + x1) / 2
        dep = 60 + 300 * depth
        for r in range(6, 0, -1):
            k = r / 6
            rx, ry = 190 * k * (0.6 + 0.4 * heat), dep * k
            col = tuple(int(HOT[i] * (1 - 0.3 * k) + 255 * 0.3 * k) for i in range(3))
            X0, Y0 = cxy(C0, cx - rx, y - 4)
            X1, Y1 = cxy(C0, cx + rx, y + ry)
            d.chord((X0, Y0 - (Y1 - Y0), X1, Y1), 0, 180, fill=col + (int(90 * heat),))


def clock(d, cx, cy, R, prog):
    circ(d, C0, cx, cy, R + 12, fill=(60, 70, 110, 255))
    circ(d, C0, cx, cy, R, fill=(246, 248, 252, 255))
    if prog > 0:  # filled sweep = elapsed time
        X0, Y0 = cxy(C0, cx - R * 0.9, cy - R * 0.9); X1, Y1 = cxy(C0, cx + R * 0.9, cy + R * 0.9)
        d.pieslice((X0, Y0, X1, Y1), -90, -90 + 360 * prog, fill=HOT + (110,))
    for k in range(12):
        a = k * math.pi / 6
        d.line([cxy(C0, cx + R * 0.82 * math.sin(a), cy - R * 0.82 * math.cos(a)), cxy(C0, cx + R * 0.95 * math.sin(a), cy - R * 0.95 * math.cos(a))],
               fill=INK + (255,), width=lw(6))
    a = 2 * math.pi * prog
    d.line([cxy(C0, cx, cy), cxy(C0, cx + R * 0.75 * math.sin(a), cy - R * 0.75 * math.cos(a))], fill=INK + (255,), width=lw(12))
    circ(d, C0, cx, cy, 14, fill=INK + (255,))


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: one hot pack in the middle, slow zoom, heat waves; 2.3 s beat: red mark on skin below it
    panel(d, BG1)
    z = 1.0 + 0.10 * ez(r / 2.0)
    hotpack(im, d, 540, 840, 0.95 * z, r)
    if r > 2.3:
        emo(im, 820, 1040, 110 * kpop(r, 2.35, .3), "⚠️")
        rings(d, C0, 540, 840, 230, r - 2.3, col=HOT, spread=40, rect=(150 * z, 200 * z, 50))


def sMax(r, im, d):  # 핫팩은 최고 70도까지
    panel(d, (46, 40, 76))
    v = 70 * ez(r / 1.2)
    thermo(d, 330, 420, 1040, v)
    hotpack(im, d, 700, 760, 0.75, r)
    if r > 1.2:
        pill(d, C0, 700, 1080, "최고 70℃", 76, HOT, WHITE, sc=kpop(r, 1.2, .22))


def sNoPain(r, im, d):  # 진짜 무서운 건 아프지 않다는 것
    panel(d, (52, 44, 84))
    skin(d, 150, 930, 740, r, heat=ez(r / 1.0), depth=0.25 * ez(r / 1.0))
    hotpack(im, d, 540, 610, 0.42, r, label=False)
    emo(im, 300, 420, 140 * kpop(r, 0.15, .3), "😌")
    if r > 0.7:
        pill(d, C0, 640, 420, "안 아파요", 64, WHITE, INK, sc=kpop(r, 0.7))
    if r > 1.6:
        stamp(d, C0, 540, 1150, "그래서 모르고 둬요", r, 1.6, HOT, 54)


def sTwoHours(r, im, d):  # 같은 자리에 두 시간
    panel(d, BG1)
    prog = ez(r / 1.6)
    clock(d, 300, 520, 170, prog * 2 / 12)
    pill(d, C0, 300, 760, "2시간", 70, YEL, INK, sc=kpop(r, 0.2))
    skin(d, 520, 960, 600, r, heat=0.4 + 0.6 * prog, depth=0.15 + 0.85 * prog)
    hotpack(im, d, 740, 500, 0.3, r, label=False)
    if r > 1.4:
        emo(im, 740, 1100, 110 * kpop(r, 1.4, .3), "🔥")
        pill(d, C0, 540, 1150, "깊은 곳까지", 58, HOT, WHITE, sc=kpop(r, 1.5))


def shirt(d, cx, cy, s=1.0):
    col = (110, 150, 220, 255)
    pts = [(-260, -300), (-120, -340), (-60, -300), (60, -300), (120, -340), (260, -300), (360, -120), (260, -60), (230, -150),
           (230, 340), (-230, 340), (-230, -150), (-260, -60), (-360, -120)]
    d.polygon([cxy(C0, cx + x * s, cy + y * s) for x, y in pts], fill=col)
    d.arc([*cxy(C0, cx - 60 * s, cy - 340 * s), *cxy(C0, cx + 60 * s, cy - 250 * s)], 0, 180, fill=(80, 110, 180, 255), width=lw(10))


def sClothes(r, im, d):  # 옷 위라도 한 곳에 오래 두면
    panel(d, (40, 50, 84))
    shirt(d, 540, 800, 1.0)
    k = ez((r - 0.6) / 1.4)
    for i in range(5, 0, -1):
        circ(d, C0, 470, 760, 60 + 40 * i * k, fill=HOT + (int(40 * k),))
    hotpack(im, d, 470, 760, 0.42, r, label=False)
    pill(d, C0, 540, 420, "옷 위라도", 62, WHITE, INK, sc=kpop(r, 0.1))
    if r > 1.2:
        pill(d, C0, 760, 1090, "한 곳에 오래", 56, HOT, WHITE, sc=kpop(r, 1.2))


def sSleep(r, im, d):  # 붙이고 자면 안 돼요, 이불 속도
    panel(d, (30, 36, 64))
    rr(d, C0, 160, 820, 920, 1000, 40, fill=(150, 120, 90, 255))           # bed frame
    rr(d, C0, 180, 700, 340, 800, 40, fill=(245, 245, 250, 255))           # pillow
    emo(im, 280, 690, 150, "😴")
    rr(d, C0, 300, 720, 900, 860, 60, fill=(120, 160, 230, 255))           # blanket
    a = kpop(r, 0.4)
    if a > 0:
        hotpack(im, d, 640, 790, 0.28 * a, r, label=False)
    emo(im, 860, 420, 60, "💤", a=0.8)
    if r > 1.0:
        X, Y = cxy(C0, 540, 760); R = 300 * kpop(r, 1.0, .25) * C0[0] * SC
        d.line([(X - R, Y - R), (X + R, Y + R)], fill=HOT + (255,), width=lw(22))
        d.line([(X - R, Y + R), (X + R, Y - R)], fill=HOT + (255,), width=lw(22))
    if r > 1.6:
        pill(d, C0, 540, 1120, "이불 속도 위험", 58, YEL, INK, sc=kpop(r, 1.6))


def sMove(r, im, d):  # 옷 위에 붙이고, 자리를 자주 옮기세요
    panel(d, (40, 60, 90))
    shirt(d, 540, 820, 0.95)
    spots = [(420, 700), (660, 760), (480, 960), (640, 1000)]
    ph = r / 0.55
    i = int(ph) % len(spots); j = (i + 1) % len(spots); f = ez(ph - int(ph))
    x = spots[i][0] + (spots[j][0] - spots[i][0]) * f
    y = spots[i][1] + (spots[j][1] - spots[i][1]) * f
    for k, (sx, sy) in enumerate(spots):
        circ(d, C0, sx, sy, 16, fill=(255, 255, 255, 120))
    hotpack(im, d, x, y, 0.34, r, label=False)
    emo(im, 820, 430, 100 * kpop(r, 0.2, .3), "🔄")
    badge(d, C0, 260, 430, 60, GREEN, "check", kpop(r, 0.9, .25))


def sParents(r, im, d):  # 어르신은 뜨거운 걸 잘 못 느끼세요 → 부모님께
    panel(d, (46, 40, 76))
    emo(im, 400, 760, 260 * kpop(r, 0.1, .3), "👵")
    emo(im, 690, 760, 260 * kpop(r, 0.3, .3), "👴")
    hotpack(im, d, 540, 1030, 0.3, r, label=False)
    if r > 1.1:
        emo(im, 860, 450, 140 * kpop(r, 1.1, .3), "📲")
        rings(d, C0, 860, 450, 70, r - 1.1, col=YEL, spread=40)
    if r > 2.5:  # H5: one more beat in the long line
        pill(d, C0, 540, 430, "부모님께 공유", 60, YEL, INK, sc=kpop(r, 2.5))
        emo(im, 545, 620, 110 * kpop(r, 2.7, .3), "❤️")


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 핫팩
    panel(d, BG1)
    hotpack(im, d, 540, 840, 0.95 * 1.1, r)
    emo(im, 840, 420, 120 * kpop(r, 0.3, .25), "🔔")


SPOKEN = [
    "핫팩, 뜨겁지 않아도 화상 입어요. 사십 도에서도요.",
    "핫팩은 최고 칠십 도까지 올라가요.",
    "진짜 무서운 건, 아프지 않다는 거예요.",
    "같은 자리에 두 시간이면, 저온화상이 생겨요.",
    "옷 위라도, 한 곳에 오래 두면 위험해요.",
    "붙이고 자면 안 돼요. 이불 속에 넣어 둔 것도요.",
    "옷 위에 붙이고, 자리를 자주 옮겨 주세요.",
    "어르신은 뜨거운 걸 잘 못 느끼세요. 부모님께 꼭 보내 드리세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (2, 5)
LINES = [
    ("", None, None, sHook),
    ("", [("핫팩은 최고", W_)], [("70도", Y_), ("까지 올라가요", W_)], sMax),
    ("", [("진짜 무서운 건", W_)], [("아프지 않다", Y_), ("는 거예요", W_)], sNoPain),
    ("", [("같은 자리에 ", W_), ("2시간", Y_)], [("저온화상", Y_), ("이 생겨요", W_)], sTwoHours),
    ("", [("옷 위라도", W_)], [("한 곳에 오래", Y_), (" 두면 위험", W_)], sClothes),
    ("", [("붙이고 ", W_), ("자면 안 돼요", Y_)], [("이불 속", Y_), ("에 넣어 둔 것도", W_)], sSleep),
    ("", [("옷 위에 붙이고", W_)], [("자리를 자주 ", W_), ("옮기세요", Y_)], sMove),
    ("", [("어르신은 뜨거운 걸 잘 못 느껴요", W_)], [("부모님께", Y_), (" 꼭 보내 드리세요", W_)], sParents),
    ("", [("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드려요", W_)], sEnd),
]
T = (("핫팩", Y_), (" 40도의 함정", W_))
Q = [[[("핫팩,", W_)], [("뜨겁지 않아도", W_)]], [[("화상", Y_)], [("입어요", W_)]]]
EV = lambda s: [("pop", s[0] + 0.12, 700), ("pop", s[0] + 0.75, 700), ("pop", s[0] + 1.4, 800), ("pop", s[0] + 1.72, 700), ("pop", s[0] + 2.5, 1200), ("pop", s[0] + 2.35, 900),
                ("whoosh", s[1] + 0.05), ("pop", s[1] + 0.9, 900),
                ("thud", s[2] + 0.1, .5), ("pop", s[2] + 0.7, 800), ("pop", s[2] + 1.6, 900),
                ("pop", s[3] + 0.2, 800), ("thud", s[3] + 1.4, .5),
                ("pop", s[4] + 0.1, 700), ("pop", s[4] + 1.2, 900),
                ("pop", s[5] + 0.4, 700), ("thud", s[5] + 1.0, .5), ("pop", s[5] + 1.6, 900),
                ("whoosh", s[6] + 0.05), ("yes", s[6] + 0.9),
                ("pop", s[7] + 0.1, 800), ("pop", s[7] + 0.3, 900), ("pop", s[7] + 1.1, 1000),
                ("pop", s[8] + 0.3, 1000)]
EP = build(43, "ep43", LINES, T, Q, EV, qsize=96, qys=(1380, 1480), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img, F, IY0, SHIFT
_cq = EP.center_q


def _center_q(im, t):  # H14: the number '40℃' huge on screen from frame 0 (emphasis = the number)
    if t >= EP.qend:
        return
    # same as kit.center_q but without dimming the picture (the hot pack must stay bright from frame 0)
    out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
    rows, ys, size = EP.qhook
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size); idx = 0
    hits = [0.12, 0.75, 1.4, 1.72]  # word-by-word 'pang' timed to the spoken first sentence
    for words, cy in zip(rows, ys):
        ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) for w in words]
        sp = size * 0.34; x = 540 - (sum(ws) + sp * (len(ws) - 1)) / 2
        for w, ww in zip(words, ws):
            lt = t - hits[min(idx, len(hits) - 1)]; idx += 1
            if lt >= 0:
                sc = 1 + 0.18 * (1 - ease(lt / 0.2))
                put(im, line_img(tuple(w), size), x + ww / 2, cy + EP.ptop - (IY0 + SHIFT), out * ease(lt / 0.08), sc)
            x += ww + sp
    if True:
        out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
        t40 = 2.5  # the number lands with the spoken '사십 도' (strongest pang, H17)
        k40 = back((t - t40) / 0.3) if t >= t40 else 0.0
        if k40 > 0:
            put(im, line_img((("40℃", Y_),), 230), 540, 400, out * ease((t - t40) / 0.08), (0.4 + 0.6 * k40) * (1 + 0.25 * (1 - ease((t - t40) / 0.3))) * (1 + 0.03 * math.sin(t * 9)))


EP.center_q = _center_q
if __name__ == "__main__":
    main(EP, "e43")
