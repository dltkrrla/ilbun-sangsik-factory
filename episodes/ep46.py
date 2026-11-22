"""46편 - 양치하고 물로 열 번 헹구면 손해예요 (치약 핵심 성분 불소를 버림) (불소: 뱉기만, 헹구지 않기)
주제 아레나 2026-11-22 (100개, 10관점 서브에이전트) 우승: '양치 후 헹구면 불소 씻김'(몸, 4기준 5·5·5·5).
결승 상대 '가습기에 정수기 물'(19). 8강 이상은 docs/ARENA.md 참고.
사실:
- 양치 뒤 남은 치약은 뱉고, 바로 물로 헹구지 않는다 — 헹구면 남은 치약 속 진한 불소가 씻겨 예방 효과가 줄어든다.
  양치 직후 가글(불소 가글 포함)도 하지 않는다 (NHS "How to keep your teeth clean", 2025-06-30 검토
  https://www.nhs.uk/live-well/healthy-teeth-and-gums/how-to-keep-your-teeth-clean/)
- 대한예방치과·구강보건학회: "물 양치를 심하게 하면 불소가 모두 씻겨 나가고 충치 예방 효과를 기대할 수 없다", 불소는 치약의
  가장 중요한 기능 성분 (스포츠경향 2014-11-13 https://sports.khan.co.kr/article/201411131738443)
- 치과 전문의 권고: 물 한 모금 정도로 가볍게 10초 내외만 헹구기 (뉴스와 2026-09-29
  https://www.news-wa.com/amp/life/health/2026/09/29/20260929500009) · 코메디닷컴 2026-10-16 https://kormedi.com/2884328/
그대로: 평면 그림 · steady 목소리 · 첫 문장 숫자 손해형(H14) · 단어별 팡, 강조 단어에 가장 크게(H17) ·
6초 같은 대상 안 첫 보상(H16) · 첫 장면 가운데 컵 하나(H15) · 끝 = 첫 장면(H13).
바꿀 것 1개: 매일 하는 '습관'을 고치는 주제(물건 원리가 아니라 행동) → 공유('가족한테') 기대."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
TOOTH = (250, 250, 246)
TOOTH2 = (214, 220, 230)
WATER = (120, 190, 255)
FLU = (90, 220, 170)
PASTE = (110, 200, 255)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def lw(v):
    return max(2, int(v * C0[0] * SC))


def tooth(d, cx, cy, s=1.0, col=TOOTH):
    """Big molar: rounded crown + two roots."""
    P = lambda x, y: cxy(C0, cx + x * s, cy + y * s)
    d.polygon([P(-150, 40), P(-120, 300), P(-70, 300), P(-30, 120), P(30, 120), P(70, 300), P(120, 300), P(150, 40)], fill=TOOTH2 + (255,))
    rr(d, C0, cx - 190 * s, cy - 190 * s, cx + 190 * s, cy + 110 * s, 110 * s, fill=col + (255,))
    for x in (-95, 0, 95):
        circ(d, C0, cx + x * s, cy - 175 * s, 70 * s, fill=col + (255,))
    X0, Y0 = P(-120, -60); X1, Y1 = P(-60, 20)
    d.ellipse((X0, Y0, X1, Y1), fill=(255, 255, 255, 200))


def fdots(d, cx, cy, s, k, t, off=(0, 0), a=1.0):
    """Fluoride 'F' badges sitting on the tooth surface; k = how many remain (0..1)."""
    pts = [(-150, -150), (-60, -210), (40, -210), (140, -150), (-180, -40), (180, -40), (-150, 60), (150, 60), (0, -60)]
    n = int(round(len(pts) * k))
    for i, (x, y) in enumerate(pts[:n]):
        bx = cx + (x + off[0] * (1 + i % 3)) * s
        by = cy + (y + off[1] * (1 + i % 2)) * s + 6 * math.sin(t * 5 + i)
        circ(d, C0, bx, by, 34 * s, fill=FLU + (int(255 * a),))
        txt(d, C0, bx, by, "F", max(8, int(40 * s)), INK)


def cup(d, cx, cy, s=1.0, level=0.6, t=0.0):
    P = lambda x, y: cxy(C0, cx + x * s, cy + y * s)
    d.polygon([P(-150, -200), P(150, -200), P(115, 210), P(-115, 210)], fill=(220, 235, 250, 255))
    top = -200 + 380 * (1 - level)
    wv = [P(-150 + 35 * (top + 200) / 410 + u * (300 - 70 * (top + 200) / 410) / 12, top + 10 * math.sin(u * 1.2 + t * 7)) for u in range(13)]
    d.polygon(wv + [P(115, 210), P(-115, 210)], fill=WATER + (255,))
    d.line([P(-150, -200), P(-115, 210)], fill=(255, 255, 255, 255), width=lw(10))
    d.line([P(150, -200), P(115, 210)], fill=(255, 255, 255, 255), width=lw(10))


def counter(d, x, y, n, r, start):
    if n <= 0:
        return
    pill(d, C0, x, y, f"{n}번", 70, YEL if n < 10 else RED, INK if n < 10 else WHITE, sc=kpop(r, start))


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: cup in the middle, slow zoom, rinse counter ticking 1→10 (answer hidden)
    panel(d, BG1)
    z = 1.0 + 0.10 * ez(r / 2.8)
    cup(d, 540, 800, 1.05 * z, 0.75 - 0.05 * math.sin(r * 3), r)
    n = min(10, 1 + int(r / 0.22))
    counter(d, 540, 470, n, r, 0.22 * (n - 1))
    emo(im, 820, 1010, 150 + 8 * math.sin(r * 6), "😤", rot=-8)
    if r > 2.2:
        emo(im, 260, 1010, 130 * kpop(r, 2.2, .25), "💸")


def sFluoride(r, im, d):  # 바로 불소예요. 충치를 막는 핵심 성분
    panel(d, (46, 40, 76))
    rr(d, C0, 200, 700, 700, 860, 60, fill=(245, 245, 250, 255))
    rr(d, C0, 700, 730, 800, 830, 20, fill=(70, 120, 220, 255))
    k = ez(r / 0.8)
    rr(d, C0, 800, 755, 800 + 120 * k, 805, 25, fill=PASTE + (255,))
    txt(d, C0, 450, 780, "치약", 60, INK)
    for i in range(5):
        kk = kpop(r, 0.6 + 0.15 * i, .25)
        if kk > 0:
            x, y = 260 + i * 140, 1000 + 30 * math.sin(i * 2 + r * 4)
            circ(d, C0, x, y, 52 * kk, fill=FLU + (255,))
            txt(d, C0, x, y, "F", max(8, int(60 * kk)), INK)
    pill(d, C0, 540, 430, "불소", 90, YEL, INK, sc=kpop(r, 0.05, .35))


def sShield(r, im, d):  # 양치 뒤 입안에 남아서 충치를 막아요
    panel(d, BG1)
    tooth(d, 540, 800, 1.0)
    fdots(d, 540, 800, 1.0, ez(r / 1.0), r)
    if r > 1.0:
        rings(d, C0, 540, 760, 260, r - 1.0, col=FLU, spread=40)
        pill(d, C0, 540, 1090, "남아서 지켜요", 56, YEL, INK, sc=kpop(r, 1.0))
    emo(im, 830, 470, 110 * kpop(r, 0.4, .3), "🛡️")


def sWash(r, im, d):  # 물로 여러 번 헹구면 싹 씻겨 나가요
    panel(d, (40, 50, 84))
    tooth(d, 540, 820, 0.95)
    k = 1 - ez((r - 0.5) / 1.4)
    fdots(d, 540, 820, 0.95, max(k, 0.0), r, off=(60 * (1 - k), 90 * (1 - k)), a=max(0.2, k))
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    for j in range(3):
        ph = (r * 0.9 + j / 3) % 1.0
        y = 520 + ph * 700
        pts = [cxy(C0, 120 + u * 70, y + 25 * math.sin(u * 0.9 + r * 6 + j)) for u in range(14)]
        ld.line(pts, fill=WATER + (int(200 * (1 - ph)),), width=lw(26))
    im.alpha_composite(L)
    counter(d, 540, 430, min(10, 1 + int(r / 0.2)), r, 0.0)
    if r > 1.6:
        stamp(d, C0, 540, 1090, "불소 싹 사라짐", r, 1.6, RED, 54)


def sSpit(r, im, d):  # 영국 보건 당국: 헹구지 말고 뱉기만
    panel(d, (52, 44, 84))
    pill(d, C0, 540, 410, "영국 보건 당국(NHS)", 50, WHITE, INK, sc=kpop(r, 0.05))
    for x, ch, lab, ok, t0 in ((300, "💦", "뱉기", True, 0.3), (780, "🥛", "헹구기", False, 1.0)):
        k = kpop(r, t0)
        if k <= 0:
            continue
        rr(d, C0, x - 170 * k, 720 - 210 * k, x + 170 * k, 720 + 210 * k, 40 * k, fill=(250, 250, 252, 255))
        emo(im, x, 680, 170 * k, ch)
        txt(d, C0, x, 860, lab, max(8, int(54 * k)), INK)
        badge(d, C0, x + 140 * k, 545, 50 * k, GREEN if ok else RED, "check" if ok else "x", min(1.0, k))
    if r > 2.2:
        pill(d, C0, 540, 1090, "뱉기만!", 70, YEL, INK, sc=kpop(r, 2.2))


def sKorea(r, im, d):  # 우리나라 치과 학회도
    panel(d, (40, 60, 90))
    pill(d, C0, 540, 410, "대한예방치과·구강보건학회", 46, WHITE, INK, sc=kpop(r, 0.05))
    tooth(d, 540, 820, 0.85)
    fdots(d, 540, 820, 0.85, 0.2, r)
    emo(im, 790, 600, 130 * kpop(r, 0.5, .3), "😢")
    if r > 1.3:
        stamp(d, C0, 540, 1090, "충치 예방 효과 ↓", r, 1.3, RED, 54)


def sSip(r, im, d):  # 찝찝하면 물 한 모금으로 가볍게
    panel(d, BG1)
    cup(d, 540, 780, 0.9, 0.18, r)
    if r > 0.4:
        pill(d, C0, 540, 420, "물 한 모금", 80, YEL, INK, sc=kpop(r, 0.4, .35))
    if r > 1.2:
        pill(d, C0, 540, 1090, "가볍게 한 번", 56, WHITE, INK, sc=kpop(r, 1.2))
        badge(d, C0, 800, 560, 56, GREEN, "check", kpop(r, 1.3, .3))


def sGargle(r, im, d):  # 양치 직후 가글도 바로 하지 마세요
    panel(d, (60, 44, 64))
    rr(d, C0, 400, 540, 680, 1000, 50, fill=(90, 200, 220, 255))
    rr(d, C0, 470, 470, 610, 560, 20, fill=(240, 240, 245, 255))
    txt(d, C0, 540, 770, "가글", 66, INK)
    badge(d, C0, 700, 520, 70, RED, "x", kpop(r, 0.6, .3))
    if r > 0.9:
        pill(d, C0, 540, 1090, "양치 직후엔 X", 58, YEL, INK, sc=kpop(r, 0.9))


def sShare(r, im, d):  # 가족한테도 꼭 보내 주세요
    panel(d, (46, 40, 76))
    emo(im, 300, 780, 200 * kpop(r, 0.1, .3), "👨")
    emo(im, 540, 760, 220 * kpop(r, 0.3, .3), "👵")
    emo(im, 780, 780, 200 * kpop(r, 0.5, .3), "🧒")
    if r > 0.9:
        emo(im, 860, 450, 140 * kpop(r, 0.9, .3), "📲")
        rings(d, C0, 860, 450, 70, r - 0.9, col=YEL, spread=40)
    if r > 1.3:
        pill(d, C0, 540, 1100, "가족한테 보내기", 60, YEL, INK, sc=kpop(r, 1.3))


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 컵
    panel(d, BG1)
    cup(d, 540, 800, 1.1, 0.75 - 0.05 * math.sin(r * 3), r)
    emo(im, 820, 1010, 150 * kpop(r, 0.2, .25), "😤", rot=-8)
    emo(im, 840, 420, 120 * kpop(r, 0.5, .25), "🔔")


SPOKEN = [
    "양치하고 물로 열 번 헹구면, 손해예요.",
    "충치를 막는 치약 핵심 성분, 불소를 버리거든요.",
    "불소는 양치 뒤에도 입안에 남아서, 충치를 막아 줘요.",
    "그런데 물로 여러 번 헹구면, 남은 불소가 싹 씻겨 나가요.",
    "그래서 영국 보건 당국은, 헹구지 말고 뱉기만 하라고 해요.",
    "우리나라 예방치과 학회도, 심하게 헹구면 효과가 없대요.",
    "찝찝하다면, 물 한 모금으로 가볍게만 헹구세요.",
    "양치 직후 가글도, 바로는 하지 마세요.",
    "가족한테도 꼭 보내 주세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 10
BREATHS = (3, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("충치 막는 ", W_), ("핵심 성분", Y_)], [("불소", Y_), ("를 버리거든요", W_)], sFluoride),
    ("", [("양치 뒤에도 ", W_), ("입안에 남아서", Y_)], [("충치를 막아 줘요", W_)], sShield),
    ("", [("물로 ", W_), ("여러 번", Y_), (" 헹구면", W_)], [("남은 불소가 ", W_), ("싹 씻겨 나가요", Y_)], sWash),
    ("", [("영국 보건 당국은", W_)], [("헹구지 말고 ", W_), ("뱉기만", Y_)], sSpit),
    ("", [("우리나라 ", W_), ("예방치과 학회", Y_), ("도", W_)], [("심하게 헹구면 ", W_), ("효과 없다", Y_)], sKorea),
    ("", [("찝찝하다면", W_)], [("물 ", W_), ("한 모금", Y_), ("으로 가볍게", W_)], sSip),
    ("", [("양치 직후 ", W_), ("가글", Y_), ("도", W_)], [("바로는 하지 마세요", W_)], sGargle),
    ("", [("가족한테도", W_)], [("꼭 ", W_), ("보내 주세요", Y_)], sShare),
    ("", [("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드려요", W_)], sEnd),
]
T = (("양치 후 물로 10번 헹구면", W_), (" 손해", Y_))
Q = [[[("물로", W_)], [("10번", Y_)], [("헹구면", W_)]], [[("손해", Y_)]]]
EV = lambda s: [("pop", s[0] + 0.05, 700), ("pop", s[0] + 0.5, 800), ("pop", s[0] + 1.0, 1100), ("pop", s[0] + 1.7, 1100),
                ("whoosh", s[1] + 0.05), ("pop", s[1] + 0.1, 1000), ("pop", s[1] + 0.8, 800), ("pop", s[1] + 1.6, 900),
                ("pop", s[2] + 0.4, 800), ("yes", s[2] + 1.0),
                ("whoosh", s[3] + 0.4), ("whoosh", s[3] + 1.2), ("thud", s[3] + 1.6, .5),
                ("pop", s[4] + 0.1, 700), ("yes", s[4] + 0.3), ("no", s[4] + 1.0), ("pop", s[4] + 2.2, 1000),
                ("pop", s[5] + 0.1, 700), ("thud", s[5] + 1.3, .5),
                ("pop", s[6] + 0.4, 900), ("yes", s[6] + 1.3),
                ("no", s[7] + 0.6), ("pop", s[7] + 0.9, 800),
                ("pop", s[8] + 0.1, 800), ("pop", s[8] + 0.9, 1000), ("yes", s[8] + 1.3),
                ("pop", s[9] + 0.3, 1000)]
EP = build(46, "ep46", LINES, T, Q, EV, qsize=104, qys=(1360, 1470), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img, F, IY0, SHIFT


def _center_q(im, t):  # word-by-word pang; strongest on '10번' and '손해' (H17)
    if t >= EP.qend:
        return
    out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
    rows, ys, size = EP.qhook
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size); idx = 0
    hits = [0.05, 0.45, 0.9, 1.7]
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
    main(EP, "e46")
