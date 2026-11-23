"""47편 - 손소독제 열 번 발라도 소용없어요 (겨울 장염 노로바이러스는 알코올로 잘 안 죽음 → 비누로 30초)
주제 아레나 2026-11-23 (100개, 10관점 서브에이전트) 우승: '노로 장염엔 손소독제 소용없음'(몸, 4기준 5·5·5·5).
결승 상대 'LED 잠깐 끄는 게 이득'(17). 8강 이상은 docs/ARENA.md 참고.
사실:
- 질병관리청: 예방을 위해 손 소독제보다는 비누를 사용하여 30초 이상 손 씻기 · 일상 환경에서 사흘간 생존 ·
  국내 겨울철~이듬해 초봄(11월~3월) 주로 발생 · 오염 물품은 락스 1 : 물 50 희석액으로 닦아 소독 ·
  식재료는 85℃ 이상에서 1분 이상 익히기 (보도자료 2025-01-07 https://www.kdca.go.kr/bbs/kdca/41/215144/artclView.do,
  정책브리핑 2023-11-30 https://www.korea.kr/news/policyNewsView.do?newsId=148923276)
- "Alcohol-based hand sanitizers are ineffective against norovirus" (Penn State Health 2025-01-29
  https://www.psu.edu/news/hershey/story/medical-minute-what-works-and-what-doesnt-prevent-norovirus)
- 단단한 겉껍질 때문에 손소독제가 덜 듣는다 (TODAY/NBC 2025-01-15 https://www.nbcbayarea.com/health/norovirus-hand-sanitizer/3761255/)
- "알코올 성분의 손 소독제가 노로바이러스에는 큰 효과가 없다" (디지털데일리 2025-12-10
  https://www.ddaily.co.kr/page/view/2025121011151453211)
그대로: 평면 그림 · steady 목소리 · 첫 문장 숫자 손해형(H14) · 단어별 팡, 강조 단어에 가장 크게(H17) ·
첫 장면 가운데 손소독제 하나(H15) · 끝 = 첫 장면(H13) · 마지막 '부모님께'(L10).
바꿀 것 1개(H18): 첫 보상 줄을 2.2~3초에, 쉬운 결과어로 ("알코올로 잘 안 죽거든요"). 여는 화면은 어둡게 멈추지 않고 펌프가 계속 움직인다."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
GEL = (150, 215, 255)
VIR = (120, 210, 90)
SHELL = (70, 140, 60)
SOAP = (255, 190, 220)
WATER = (120, 190, 255)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def lw(v):
    return max(2, int(v * C0[0] * SC))


def bottle(d, cx, cy, s=1.0, press=0.0, label=True):
    """Pump bottle of hand sanitizer; press 0..1 pushes the pump head down."""
    rr(d, C0, cx - 150 * s, cy - 120 * s, cx + 150 * s, cy + 260 * s, 60 * s, fill=(225, 240, 252, 255))
    rr(d, C0, cx - 130 * s, cy - 40 * s, cx + 130 * s, cy + 240 * s, 50 * s, fill=GEL + (255,))
    if label:
        rr(d, C0, cx - 115 * s, cy + 30 * s, cx + 115 * s, cy + 170 * s, 20 * s, fill=(255, 255, 255, 255))
        txt(d, C0, cx, cy + 100 * s, "손소독제", max(8, int(46 * s)), INK)
    rr(d, C0, cx - 50 * s, cy - 175 * s, cx + 50 * s, cy - 115 * s, 12 * s, fill=(240, 240, 245, 255))
    py = cy - 175 * s + 40 * s * press
    rr(d, C0, cx - 18 * s, py - 90 * s, cx + 18 * s, py, 8 * s, fill=(250, 250, 252, 255))
    rr(d, C0, cx - 70 * s, py - 120 * s, cx + 130 * s, py - 80 * s, 16 * s, fill=(250, 250, 252, 255))


def virus(d, cx, cy, s=1.0, t=0.0, shell=0.0, a=255):
    """Green germ with spikes; shell 0..1 draws the hard outer coat."""
    for i in range(10):
        ang = i * math.pi / 5 + 0.2 * math.sin(t * 2)
        x1, y1 = cx + 120 * s * math.cos(ang), cy + 120 * s * math.sin(ang)
        circ(d, C0, x1, y1, 26 * s, fill=SHELL + (a,))
    circ(d, C0, cx, cy, 115 * s, fill=VIR + (a,))
    if shell > 0:
        X, Y = cxy(C0, cx, cy); R = 115 * s * C0[0] * SC
        d.ellipse((X - R, Y - R, X + R, Y + R), outline=(60, 90, 50, int(a * shell)), width=lw(22 * s))
    for ex in (-40, 40):
        circ(d, C0, cx + ex * s, cy - 15 * s, 16 * s, fill=(30, 40, 30, a))
    d.arc(tuple(cxy(C0, cx - 40 * s, cy + 5 * s)) + tuple(cxy(C0, cx + 40 * s, cy + 55 * s)), 10, 170, fill=(30, 40, 30, a), width=lw(8 * s))


def counter(d, x, y, n, r, start):
    if n <= 0:
        return
    pill(d, C0, x, y, f"{n}번", 70, YEL if n < 10 else RED, INK if n < 10 else WHITE, sc=kpop(r, start))


def drops(d, cx, cy, r, s=1.0, bounce=True):
    """Alcohol drops fall on the germ and bounce off."""
    for i in range(6):
        ph = (r * 1.1 + i / 6) % 1.0
        x = cx + (-200 + i * 80) * s
        if ph < 0.5:
            y = cy - 380 * s + ph / 0.5 * 260 * s
        else:
            k = (ph - 0.5) / 0.5
            y = cy - 120 * s - 160 * s * math.sin(k * math.pi)
            x += (1 if i % 2 else -1) * 220 * s * k
        circ(d, C0, x, y, 20 * s, fill=GEL + (int(255 * (1 - max(0, ph - 0.7) / 0.3)),))


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: one sanitizer bottle, slow zoom, pump keeps pressing 1→10 (germ still smiling below)
    panel(d, BG1)
    z = 1.0 + 0.10 * ez(r / 2.4)
    press = abs(math.sin(r * math.pi / 0.22))
    bottle(d, 540, 830, 1.05 * z, press)
    n = min(10, 1 + int(r / 0.2))
    counter(d, 540, 390, n, r, 0.2 * (n - 1))
    if press > 0.6:  # gel squirt from the nozzle
        circ(d, C0, 540 + 140 * z * 1.05, 830 - 200 * z * 1.05 + 60 * press, 18, fill=GEL + (255,))
    emo(im, 830, 1060, 130, "🤲")
    if r > 0.8:
        emo(im, 830, 1000 + 6 * math.sin(r * 8), 80 * kpop(r, 0.8, .25), "🦠")
    if r > 1.6:
        emo(im, 250, 1040, 120 * kpop(r, 1.6, .25), "😵")


def sAlcohol(r, im, d):  # 겨울 장염 바이러스는, 알코올로 잘 안 죽거든요
    panel(d, (46, 40, 76))
    pill(d, C0, 540, 410, "겨울 장염 바이러스", 54, WHITE, INK, sc=kpop(r, 0.05))
    virus(d, 540, 820, 1.25 + 0.03 * math.sin(r * 5), r)
    drops(d, 540, 820, r, 1.2)
    if r > 0.9:
        stamp(d, C0, 540, 1100, "알코올로 안 죽음", r, 0.9, RED, 56)


def sShell(r, im, d):  # 범인은 노로바이러스, 껍질이 단단해서 알코올을 버텨요
    panel(d, BG1)
    pill(d, C0, 540, 410, "노로바이러스", 70, YEL, INK, sc=kpop(r, 0.05, .35))
    virus(d, 540, 820, 1.2, r, shell=ez((r - 0.6) / 0.5))
    if r > 0.9:
        rings(d, C0, 540, 820, 170, r - 0.9, col=YEL, spread=40)
        emo(im, 820, 620, 110 * kpop(r, 1.0, .3), "🛡️")
    if r > 1.4:
        pill(d, C0, 540, 1100, "껍질이 단단해요", 56, WHITE, INK, sc=kpop(r, 1.4))


def sSoap(r, im, d):  # 그럼 뭘로 막냐고요? 비누로 30초 넘게 씻기
    panel(d, (40, 50, 84))
    if r < 1.0:
        txt(d, C0, 540, 760, "?", int(260 * kpop(r, 0.05, .3) + 1), YEL)
        return
    k = kpop(r, 1.0, .3)
    emo(im, 540, 760, 230 * k, "🧼")
    for i in range(7):
        ph = (r * 0.7 + i / 7) % 1.0
        x = 300 + i * 80 + 30 * math.sin(r * 3 + i)
        y = 940 - ph * 520
        X, Y = cxy(C0, x, y); R = (24 + 10 * (i % 3)) * C0[0] * SC
        d.ellipse((X - R, Y - R, X + R, Y + R), outline=(255, 255, 255, int(220 * (1 - ph))), width=lw(5))
    sec = min(30, int((r - 1.0) / 1.6 * 30)) if r > 1.0 else 0
    pill(d, C0, 540, 430, f"{max(sec, 1)}초", 90, YEL if sec < 30 else GREEN, INK, sc=kpop(r, 1.0, .35))
    if r > 2.4:
        pill(d, C0, 540, 1100, "흐르는 물에 비누로", 54, WHITE, INK, sc=kpop(r, 2.4))


def sKDCA(r, im, d):  # 질병관리청도, 소독제보다 비누를 쓰라고 해요
    panel(d, (52, 44, 84))
    pill(d, C0, 540, 410, "질병관리청", 56, WHITE, INK, sc=kpop(r, 0.05))
    for x, ch, lab, ok, t0 in ((300, "🧼", "비누", True, 0.3), (780, "🧴", "소독제", False, 0.9)):
        k = kpop(r, t0)
        if k <= 0:
            continue
        rr(d, C0, x - 170 * k, 720 - 210 * k, x + 170 * k, 720 + 210 * k, 40 * k, fill=(250, 250, 252, 255))
        emo(im, x, 680, 170 * k, ch)
        txt(d, C0, x, 860, lab, max(8, int(54 * k)), INK)
        badge(d, C0, x + 140 * k, 545, 50 * k, GREEN if ok else RED, "check" if ok else "x", min(1.0, k))
    if r > 1.6:
        pill(d, C0, 540, 1100, "비누로 30초 이상", 58, YEL, INK, sc=kpop(r, 1.6))


def sDoor(r, im, d):  # 이 바이러스, 문고리에서도 사흘이나 살아요
    panel(d, BG1)
    rr(d, C0, 160, 480, 520, 1180, 20, fill=(150, 105, 70, 255))
    rr(d, C0, 300, 780, 700, 860, 40, fill=(210, 210, 220, 255))
    circ(d, C0, 300, 820, 70, fill=(190, 190, 200, 255))
    for i, (x, y) in enumerate(((470, 800), (600, 790), (380, 840), (660, 840))):
        kk = kpop(r, 0.2 + 0.15 * i, .25)
        if kk > 0:
            virus(d, x, y + 5 * math.sin(r * 5 + i), 0.28 * kk, r)
    if r > 0.9:
        pill(d, C0, 760, 520, "3일", 110, YEL, INK, sc=kpop(r, 0.9, .35))
    if r > 1.5:
        pill(d, C0, 540, 1100, "사흘이나 살아요", 56, WHITE, INK, sc=kpop(r, 1.5))


def sBleach(r, im, d):  # 가족이 토했다면, 락스 1에 물 50으로 닦으세요
    panel(d, (60, 44, 64))
    k = kpop(r, 0.05, .3)
    rr(d, C0, 200, 620 - 200 * k, 420, 1000, 40, fill=(250, 250, 250, 255))
    rr(d, C0, 270, 560 - 200 * k, 350, 625 - 200 * k, 15, fill=(230, 80, 90, 255))
    txt(d, C0, 310, 860, "락스", max(8, int(50 * k)), INK)
    if r > 0.6:
        cup_k = kpop(r, 0.6, .3)
        rr(d, C0, 620, 1000 - 380 * cup_k, 900, 1000, 30, fill=WATER + (255,))
        txt(d, C0, 760, 880, "물", max(8, int(56 * cup_k)), INK)
    if r > 1.1:
        pill(d, C0, 540, 430, "1 : 50", 110, YEL, INK, sc=kpop(r, 1.1, .35))
    if r > 1.8:
        pill(d, C0, 540, 1100, "묻힌 천으로 닦기", 54, WHITE, INK, sc=kpop(r, 1.8))


def sOyster(r, im, d):  # 굴 같은 음식은, 85도에서 1분 넘게 익히고요
    panel(d, (46, 40, 76))
    emo(im, 380, 800, 230 * kpop(r, 0.05, .3), "🦪")
    k = ez((r - 0.5) / 1.0)
    rr(d, C0, 720, 520, 800, 1020, 40, fill=(245, 245, 250, 255))
    rr(d, C0, 735, 1000 - 460 * k, 785, 1000, 25, fill=(235, 70, 70, 255))
    circ(d, C0, 760, 1040, 60, fill=(235, 70, 70, 255))
    if r > 0.6:
        pill(d, C0, 540, 430, "85℃", 100, YEL, INK, sc=kpop(r, 0.6, .35))
    if r > 1.3:
        pill(d, C0, 540, 1100, "1분 넘게 익히기", 56, WHITE, INK, sc=kpop(r, 1.3))


def sShare(r, im, d):  # 부모님께도 꼭 보내 드리세요
    panel(d, (46, 40, 76))
    emo(im, 380, 780, 220 * kpop(r, 0.1, .3), "👴")
    emo(im, 700, 780, 220 * kpop(r, 0.3, .3), "👵")
    if r > 0.7:
        emo(im, 860, 450, 140 * kpop(r, 0.7, .3), "📲")
        rings(d, C0, 860, 450, 70, r - 0.7, col=YEL, spread=40)
    if r > 1.1:
        pill(d, C0, 540, 1100, "부모님께 보내기", 60, YEL, INK, sc=kpop(r, 1.1))


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 손소독제
    panel(d, BG1)
    bottle(d, 540, 830, 1.1, abs(math.sin(r * math.pi / 0.5)))
    emo(im, 830, 1060, 130 * kpop(r, 0.1, .25), "🤲")
    emo(im, 840, 420, 120 * kpop(r, 0.5, .25), "🔔")


SPOKEN = [
    "손소독제 열 번 발라도, 소용없어요.",
    "겨울 장염 바이러스는, 알코올로 잘 안 죽거든요.",
    "범인은 노로바이러스, 껍질이 단단해서 알코올을 버텨요.",
    "그럼 뭘로 막냐고요? 비누로, 삼십 초 넘게 씻는 거예요.",
    "질병관리청도, 소독제보다 비누를 쓰라고 해요.",
    "이 바이러스, 문고리에서도 사흘이나 살아요.",
    "가족이 토했다면, 락스 일에 물 오십으로 닦으세요.",
    "굴 같은 음식은, 팔십오 도에서 일 분 넘게 익히고요.",
    "부모님께도 꼭 보내 드리세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 10
BREATHS = (3, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("겨울 장염 바이러스는", W_)], [("알코올로 ", W_), ("잘 안 죽거든요", Y_)], sAlcohol),
    ("", [("범인은 ", W_), ("노로바이러스", Y_)], [("껍질이 단단해서 ", W_), ("버텨요", Y_)], sShell),
    ("", [("그럼 뭘로 막냐고요?", W_)], [("비누로 ", Y_), ("30초", Y_), (" 넘게", W_)], sSoap),
    ("", [("질병관리청", Y_), ("도", W_)], [("소독제보다 ", W_), ("비누", Y_)], sKDCA),
    ("", [("문고리에서도", W_)], [("사흘", Y_), ("이나 살아요", W_)], sDoor),
    ("", [("가족이 토했다면", W_)], [("락스 1 : 물 50", Y_), ("으로", W_)], sBleach),
    ("", [("굴 같은 음식은", W_)], [("85도", Y_), ("에서 ", W_), ("1분 넘게", Y_)], sOyster),
    ("", [("부모님께도", W_)], [("꼭 ", W_), ("보내 드리세요", Y_)], sShare),
    ("", [("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드려요", W_)], sEnd),
]
T = (("손소독제 10번 발라도", W_), (" 소용없는 바이러스", Y_))
Q = [[[("손소독제", W_)], [("10번", Y_)]], [[("발라도", W_)], [("소용없어요", Y_)]]]
EV = lambda s: [("pop", s[0] + 0.05, 700), ("pop", s[0] + 0.5, 800), ("pop", s[0] + 1.0, 1100), ("pop", s[0] + 1.7, 1100),
                ("whoosh", s[1] + 0.05), ("pop", s[1] + 0.1, 900), ("thud", s[1] + 0.9, .5),
                ("pop", s[2] + 0.1, 1000), ("yes", s[2] + 0.9), ("pop", s[2] + 1.4, 800),
                ("pop", s[3] + 0.1, 900), ("whoosh", s[3] + 1.0), ("pop", s[3] + 1.0, 1000), ("pop", s[3] + 2.4, 800),
                ("pop", s[4] + 0.1, 700), ("yes", s[4] + 0.3), ("no", s[4] + 0.9), ("pop", s[4] + 1.6, 1000),
                ("pop", s[5] + 0.3, 800), ("pop", s[5] + 0.9, 1100), ("pop", s[5] + 1.5, 800),
                ("pop", s[6] + 0.1, 700), ("pop", s[6] + 0.6, 800), ("pop", s[6] + 1.1, 1100), ("pop", s[6] + 1.8, 800),
                ("pop", s[7] + 0.1, 800), ("pop", s[7] + 0.6, 1000), ("pop", s[7] + 1.3, 800),
                ("pop", s[8] + 0.1, 800), ("pop", s[8] + 0.7, 1000), ("yes", s[8] + 1.1),
                ("pop", s[9] + 0.3, 1000)]
EP = build(47, "ep47", LINES, T, Q, EV, qsize=104, qys=(1360, 1470), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img, F, IY0, SHIFT


def _center_q(im, t):  # word-by-word pang; strongest on '10번' and '소용없어요' (H17)
    if t >= EP.qend:
        return
    out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
    rows, ys, size = EP.qhook
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size); idx = 0
    hits = [0.05, 0.6, 1.0, 1.4]
    strong = [0.12, 0.35, 0.12, 0.35]
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
    main(EP, "e47")
