"""44편 - 숟가락은 디귿, 젓가락은 시옷 (받침이 다른 진짜 이유)
주제 아레나 2026-11-21 2회차 (100개 후보 → 중복·사실확인 전력 13개 탈락 → 87강 토너먼트).
결승 승자 '귤 꼭지 점 = 알맹이 수'(20)는 3단계 사실 확인에서 탈락(유튜브 영상 인용 기사뿐, 연구 근거 없음) → 준우승 언어 관점 '숟가락 ㄷ·젓가락 ㅅ'(19).
사용자 피드백(11/21): "핫팩은 별로, 주제가 뻔함" → 안전 경고형이 아닌, 누구나 매일 쓰는 말의 의외의 이유.
사실:
- 한글 맞춤법 제29항: 끝소리가 ㄹ인 말과 딴 말이 어울릴 적에 ㄹ 소리가 ㄷ 소리로 나는 것은 ㄷ으로 적는다.
  예) 숟가락(술~), 섣달(설~), 이튿날(이틀~), 사흗날, 반짇고리 (국립국어원 '왜 숟가락은 ㄷ인데 젓가락은 ㅅ일까?' 정희창
  https://www.korean.go.kr/nkview/nknews/200103/32_2.htm · 한글 맞춤법 1980 제6항 예시 https://ko.wikisource.org/wiki/한글_맞춤법_(1980))
- 젓가락 = 저(箸) + ㅅ(사이시옷) + 가락 (같은 국립국어원 글)
- '술': 숟가락으로 음식을 떠 그 분량을 세는 단위 ("밥 한 술") — 표준국어대사전
그대로(지난 편과 같게): 평면 그림 · steady 목소리 · 6초 같은 물건 안의 첫 보상(H16) · 첫 장면 가운데 대상(H15) · 끝 장면 = 첫 장면(H13) · 공유 문구 → 팔로우.
바꿀 것 1개: 주제 유형 (생활 안전 경고 → 매일 쓰는 '말'의 숨은 이유, 의외성 우선)."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
CARD = (250, 248, 242)
METAL = (196, 204, 218)
METAL2 = (150, 160, 180)
WOOD = (196, 140, 86)
WOOD2 = (160, 106, 60)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def lw(v):
    return max(2, int(v * C0[0] * SC))


def card(d, x, y, s, ch, col=INK, bg=CARD, sc=1.0, size=None):
    if sc <= 0.02:
        return
    w = s * sc
    rr(d, C0, x - w / 2 + 8, y - w / 2 + 10, x + w / 2 + 8, y + w / 2 + 10, 34 * sc, fill=(0, 0, 0, 70))
    rr(d, C0, x - w / 2, y - w / 2, x + w / 2, y + w / 2, 34 * sc, fill=bg + (255,))
    txt(d, C0, x, y - 6 * sc, ch, int((size or s * 0.72) * sc), col)


def jamo_tag(d, x, y, ch, col, sc=1.0, r=62):
    if sc <= 0.02:
        return
    circ(d, C0, x, y, r * sc + 8, fill=WHITE + (255,))
    circ(d, C0, x, y, r * sc, fill=col + (255,))
    txt(d, C0, x, y - 4 * sc, ch, int(r * 1.25 * sc), WHITE)


def spoon(d, x, y, s=1.0, rot=0.0):
    """Vertical spoon: bowl on top, long handle down. rot = small tilt (radians)."""
    def P(px, py):
        c, sn = math.cos(rot), math.sin(rot)
        return cxy(C0, x + (px * c - py * sn) * s, y + (px * sn + py * c) * s)
    bowl = [P(70 * math.cos(a), -170 + 95 * math.sin(a)) for a in [i * math.pi / 20 for i in range(41)]]
    d.polygon(bowl, fill=METAL + (255,))
    inner = [P(48 * math.cos(a), -170 + 70 * math.sin(a)) for a in [i * math.pi / 20 for i in range(41)]]
    d.polygon(inner, fill=METAL2 + (255,))
    d.polygon([P(-14, -80), P(14, -80), P(20, 260), P(-20, 260)], fill=METAL + (255,))


def chopsticks(d, x, y, s=1.0, open_=0.0):
    for sgn in (-1, 1):
        a = sgn * (0.05 + 0.12 * open_)
        top = (x + sgn * 26 * s + math.sin(a) * -260 * s, y - 260 * s)
        bot = (x + sgn * 10 * s + math.sin(a) * 250 * s, y + 250 * s)
        d.line([cxy(C0, *top), cxy(C0, *bot)], fill=METAL + (255,), width=lw(22 * s))


def arrow_r(d, x0, x1, y, col=YEL, a=1.0):
    if a <= 0.02:
        return
    xe = x0 + (x1 - x0) * a
    d.line([cxy(C0, x0, y), cxy(C0, xe, y)], fill=col + (255,), width=lw(14))
    d.polygon([cxy(C0, xe + 26, y), cxy(C0, xe - 10, y - 26), cxy(C0, xe - 10, y + 26)], fill=col + (255,))


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: spoon + chopsticks side by side, slow zoom; ㄷ / ㅅ marks pop with the spoken words
    panel(d, BG1)
    z = 1.0 + 0.08 * ez(r / 2.4)
    spoon(d, 330, 760, 1.0 * z, rot=-0.08 + 0.03 * math.sin(r * 3))
    chopsticks(d, 750, 760, 1.0 * z, open_=0.5 + 0.5 * math.sin(r * 2.5))
    card(d, 330, 1020, 200, "숟", sc=1.0 if r > 0.2 else kpop(r, -0.1, .3))
    card(d, 750, 1020, 200, "젓", sc=1.0 if r > 0.2 else kpop(r, -0.05, .3))
    if r > 0.55:
        jamo_tag(d, 440, 920, "ㄷ", RED, kpop(r, 0.55, .25) * (1 + 0.05 * math.sin(r * 7)), 60)
    if r > 1.3:
        jamo_tag(d, 860, 920, "ㅅ", BLUE, kpop(r, 1.3, .25) * (1 + 0.05 * math.sin(r * 7)), 60)
    if r > 2.0:
        emo(im, 540, 500, 130 * kpop(r, 2.0, .3), "🤔")


def sSul(r, im, d):  # 숟가락의 숟은, 원래 밥 한 술의 '술'
    panel(d, (46, 40, 76))
    emo(im, 360, 900, 300 * kpop(r, 0.0, .3), "🍚")
    lift = 60 * math.sin(min(1.0, r / 1.0) * math.pi)
    spoon(d, 640, 760 - lift, 0.75, rot=0.5)
    card(d, 300, 480, 170, "숟", sc=kpop(r, 0.1, .25))
    if r > 0.7:
        arrow_r(d, 400, 560, 480, a=ease((r - 0.7) / 0.3))
        card(d, 700, 480, 200, "술", col=RED, sc=kpop(r, 0.9, .3))
    if r > 1.6:
        pill(d, C0, 540, 1130, "한 술, 두 술", 72, YEL, INK, sc=kpop(r, 1.6))


def sLtoD(r, im, d):  # 술 + 가락 → 리을이 디귿 소리로
    panel(d, BG1)
    k = ez((r - 0.2) / 0.6)
    card(d, 300 + 40 * k, 560, 200, "술", sc=kpop(r, 0.0, .25))
    txt(d, C0, 450, 560, "+", 120, WHITE)
    card(d, 720 - 40 * k, 560, 200, "가락", sc=kpop(r, 0.15, .25), size=100)
    if r > 0.9:
        jamo_tag(d, 330, 820, "ㄹ", (80, 92, 140), kpop(r, 0.9, .25), 70)
        if r > 1.4:
            X, Y = cxy(C0, 330, 820); R = 70 * C0[0] * SC
            d.line([(X - R, Y - R), (X + R, Y + R)], fill=RED + (255,), width=lw(14))
        arrow_r(d, 440, 600, 820, a=ease((r - 1.5) / 0.3))
        if r > 1.8:
            jamo_tag(d, 720, 820, "ㄷ", RED, kpop(r, 1.8, .3), 80)
    if r > 2.3:
        pill(d, C0, 540, 1100, "[숟까락]", 70, YEL, INK, sc=kpop(r, 2.3))


def sFamily(r, im, d):  # 섣달, 이튿날도 똑같아요
    panel(d, (40, 50, 84))
    rows = [("설+달", "섣달", 0.1), ("이틀+날", "이튿날", 0.9), ("술+가락", "숟가락", 1.7)]
    for i, (a, b, t0) in enumerate(rows):
        y = 470 + i * 260
        if r > t0:
            pill(d, C0, 300, y, a, 64, (70, 80, 120), WHITE, sc=kpop(r, t0))
            arrow_r(d, 470, 590, y, a=ease((r - t0 - 0.2) / 0.25))
            if r > t0 + 0.4:
                pill(d, C0, 790, y, b, 74, YEL, INK, sc=kpop(r, t0 + 0.4))


def sJeo(r, im, d):  # 그럼 젓가락은요? 저는 한자로 젓가락 저(箸)
    panel(d, (52, 44, 84))
    chopsticks(d, 540, 820, 0.95, open_=0.5 + 0.5 * math.sin(r * 3))
    card(d, 540, 460, 200, "젓", sc=kpop(r, 0.0, .25))
    emo(im, 830, 450, 120 * kpop(r, 0.2, .3), "❓")
    if r > 1.2:
        card(d, 300, 1080, 170, "저", col=BLUE, sc=kpop(r, 1.2, .3))
        arrow_r(d, 410, 590, 1080, a=ease((r - 1.4) / 0.3))
        card(d, 760, 1080, 190, "箸", col=INK, sc=kpop(r, 1.6, .3))


def sSaisiot(r, im, d):  # 저와 가락 사이에 사이시옷
    panel(d, BG1)
    gap = 120 * (1 - ez((r - 1.6) / 0.5))
    card(d, 300 - gap * 0.5, 560, 190, "저", sc=kpop(r, 0.0, .25))
    card(d, 780 + gap * 0.5, 560, 190, "가락", sc=kpop(r, 0.1, .25), size=96)
    if r > 0.6:
        jamo_tag(d, 540, 560, "ㅅ", BLUE, kpop(r, 0.6, .3) * (1 + 0.08 * math.sin(r * 8)), 70)
        rings(d, C0, 540, 560, 80, r - 0.6, col=YEL, spread=40)
    if r > 2.0:
        pill(d, C0, 540, 820, "사이시옷", 78, YEL, INK, sc=kpop(r, 2.0))
    if r > 2.4:
        card(d, 540, 1020, 170, "젓", col=BLUE, sc=kpop(r, 2.4, .3))


def sSummary(r, im, d):  # 그래서 숟가락은 디귿, 젓가락은 시옷
    panel(d, (40, 60, 90))
    spoon(d, 320, 720, 0.85)
    chopsticks(d, 760, 720, 0.85)
    card(d, 320, 1040, 170, "숟", sc=kpop(r, 0.1, .25))
    card(d, 760, 1040, 170, "젓", sc=kpop(r, 0.6, .25))
    if r > 0.3:
        pill(d, C0, 320, 430, "술 → ㄷ", 58, RED, WHITE, sc=kpop(r, 0.3))
    if r > 0.9:
        pill(d, C0, 760, 430, "저 + ㅅ", 58, BLUE, WHITE, sc=kpop(r, 0.9))
    if r > 1.5:
        badge(d, C0, 540, 760, 60, GREEN, "check", kpop(r, 1.5, .25))


def sShare(r, im, d):  # 맞춤법 헷갈리는 친구에게 보내 주세요
    panel(d, (46, 40, 76))
    emo(im, 380, 760, 240 * kpop(r, 0.1, .3), "🙋")
    emo(im, 700, 760, 240 * kpop(r, 0.3, .3), "🤷")
    if r > 0.9:
        emo(im, 860, 450, 140 * kpop(r, 0.9, .3), "📲")
        rings(d, C0, 860, 450, 70, r - 0.9, col=YEL, spread=40)
    if r > 1.6:
        pill(d, C0, 540, 1080, "숟? 숫? 헷갈리는 친구", 52, YEL, INK, sc=kpop(r, 1.6))
    if r > 2.4:
        emo(im, 300, 450, 110 * kpop(r, 2.4, .3), "🥄")


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 숟가락·젓가락
    panel(d, BG1)
    spoon(d, 330, 760, 1.08, rot=-0.08 + 0.03 * math.sin(r * 3))
    chopsticks(d, 750, 760, 1.08, open_=0.5 + 0.5 * math.sin(r * 2.5))
    card(d, 330, 1040, 190, "숟")
    card(d, 750, 1040, 190, "젓")
    emo(im, 540, 480, 120 * kpop(r, 0.3, .25), "🔔")


SPOKEN = [
    "숟가락은 디귿, 젓가락은 시옷. 받침이 다른 데는 이유가 있어요.",
    "숟가락의 숟은, 원래 한 술 두 술 할 때, 그 술이에요.",
    "술에 가락이 붙으면서, 리을이 디귿 소리로 바뀌었어요.",
    "섣달, 이튿날도 똑같아요. 설과 이틀이 바뀐 거죠.",
    "그럼 젓가락은요? 저는 한자로, 젓가락 저예요.",
    "저와 가락 사이에, 사이시옷이 들어간 거예요.",
    "그래서 숟가락은 디귿, 젓가락은 시옷!",
    "맞춤법 헷갈리는 친구에게, 꼭 보내 주세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (2, 5)
LINES = [
    ("", None, None, sHook),
    ("", [("숟가락의 숟은", W_)], [("한 ", W_), ("술", Y_), (" 두 ", W_), ("술", Y_), (" 할 때 그 술", W_)], sSul),
    ("", [("술 + 가락", W_)], [("ㄹ", Y_), ("이 ", W_), ("ㄷ 소리", Y_), ("로 바뀌어요", W_)], sLtoD),
    ("", [("섣달", Y_), (", ", W_), ("이튿날", Y_), ("도", W_)], [("설·이틀이 바뀐 거예요", W_)], sFamily),
    ("", [("그럼 ", W_), ("젓가락", Y_), ("은요?", W_)], [("저", Y_), (" = 한자 젓가락 저(箸)", W_)], sJeo),
    ("", [("저", W_), (" + ", W_), ("ㅅ", Y_), (" + 가락", W_)], [("사이시옷", Y_), ("이 들어갔어요", W_)], sSaisiot),
    ("", [("숟가락은 ", W_), ("ㄷ", Y_)], [("젓가락은 ", W_), ("ㅅ", Y_)], sSummary),
    ("", [("맞춤법 헷갈리는 친구에게", W_)], [("꼭 ", W_), ("보내 주세요", Y_)], sShare),
    ("", [("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드려요", W_)], sEnd),
]
T = (("숟가락은 ㄷ, 젓가락은 ㅅ", Y_), (" 받침이 다른 이유", W_))
Q = [[[("숟가락은", W_)], [("ㄷ", Y_)]], [[("젓가락은", W_)], [("ㅅ", Y_)]]]
EV = lambda s: [("pop", s[0] + 0.05, 700), ("pop", s[0] + 0.55, 1000), ("pop", s[0] + 0.7, 700), ("pop", s[0] + 1.3, 1100), ("pop", s[0] + 2.0, 800),
                ("whoosh", s[1] + 0.05), ("pop", s[1] + 0.9, 900), ("pop", s[1] + 1.6, 900),
                ("pop", s[2] + 0.1, 700), ("pop", s[2] + 0.9, 800), ("thud", s[2] + 1.4, .5), ("pop", s[2] + 1.8, 1000),
                ("pop", s[3] + 0.5, 800), ("pop", s[3] + 1.3, 900), ("yes", s[3] + 2.4),
                ("whoosh", s[4] + 0.05), ("pop", s[4] + 1.2, 800), ("pop", s[4] + 1.6, 900),
                ("pop", s[5] + 0.1, 700), ("pop", s[5] + 0.6, 1100), ("pop", s[5] + 2.0, 900),
                ("pop", s[6] + 0.3, 800), ("pop", s[6] + 0.9, 900), ("yes", s[6] + 1.5),
                ("pop", s[7] + 0.1, 800), ("pop", s[7] + 0.9, 1000), ("pop", s[7] + 1.6, 900),
                ("pop", s[8] + 0.3, 1000)]
EP = build(44, "ep44", LINES, T, Q, EV, qsize=110, qys=(1380, 1490), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img, F, IY0, SHIFT


def _center_q(im, t):  # word-by-word pang on the first sentence; strongest pang on the two jamo (H17)
    if t >= EP.qend:
        return
    out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
    rows, ys, size = EP.qhook
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size); idx = 0
    hits = [0.05, 0.55, 0.7, 1.3]
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
    main(EP, "e44")
