"""28편 - 도시가스 냄새의 정체 (원래 냄새 0 → 1937년 미국 뉴런던 학교 폭발 → 일부러 넣는 부취제)
주제 아레나 2026-11-18 우승 후보 '샴푸 통 톱니'가 사실 확인에서 한국 샴푸엔 일반적이지 않아(보편성 H0 미달) 결승 상대였던 이 주제로 진행.
사실:
- 도시가스(LNG) 주성분 메탄은 색·냄새가 없고, 새는 걸 알아채도록 냄새 물질(부취제)을 일부러 넣는다. 우리나라 법도 부취제 첨가를 규정
  (주간경향 2016-08-09 https://weekly.khan.co.kr/article/201608091750411 · 도시가스사업법 시행규칙 제2조 '부취제 주입설비').
  냄새 묘사 "양파 썩은 냄새, 계란 썩은 냄새" (경기일보 2016-07-28 https://www.kyeonggi.com/article/201607280868619)
- 1937-03-18 미국 텍사스 뉴런던 학교: 냄새 없는 가스가 새어 폭발, 약 300명 사망. 이후 주 법으로 가스에 냄새 첨가 의무화
  (HISTORY https://www.history.com/this-day-in-history/march-18/natural-gas-explosion-kills-schoolchildren-in-texas)
- 냄새 날 때: 전기 스위치·환풍기 만지지 말고, 밸브 잠그고, 손으로 창문 열기 (한국가스안전공사 안내 인용, 위키트리
  https://www.wikitree.co.kr/articles/1173766)
바꿀 것 1개(플레이북 H14): 첫 문장 = 숫자 하나가 든 단정형("원래 냄새는 제로"), 0초 화면에 큰 '0'. 3D 렌더러(Blender)를 이 환경에서
받을 수 없어 26편처럼 평면 그림."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
FLAME = (80, 150, 255)
FLAME2 = (170, 215, 255)
STEEL = (70, 76, 92)
GASC = (150, 230, 140)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def layer(im):
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); return L, ImageDraw.Draw(L)


def burner(im, d, cx, cy, s, r, lit=True, knob=True):
    """Gas-stove burner seen from slightly above: grate, ring, flickering blue flames."""
    rr(d, C0, cx - 400 * s, cy - 250 * s, cx + 400 * s, cy + 250 * s, 60 * s, fill=(24, 26, 34, 255))
    circ(d, C0, cx, cy, 190 * s, fill=(46, 48, 58, 255))
    for a in range(4):  # grate arms
        ang = a * math.pi / 2 + math.pi / 4
        x1, y1 = cx + math.cos(ang) * 230 * s, cy + math.sin(ang) * 160 * s
        d.line([cxy(C0, cx + math.cos(ang) * 120 * s, cy + math.sin(ang) * 84 * s), cxy(C0, x1, y1)], fill=(90, 92, 104, 255), width=max(3, int(26 * s * C0[0] * SC)))
    circ(d, C0, cx, cy, 120 * s, fill=STEEL + (255,))
    circ(d, C0, cx, cy, 70 * s, fill=(36, 38, 46, 255))
    if lit:
        L, ld = layer(im)
        n = 18
        for i in range(n):
            ang = i * 2 * math.pi / n
            fl = 1 + 0.25 * math.sin(r * 17 + i * 1.9)
            bx, by = cx + math.cos(ang) * 120 * s, cy + math.sin(ang) * 84 * s
            tip = (bx + math.cos(ang) * 30 * s, by + math.sin(ang) * 20 * s - 70 * s * fl)
            l1 = (bx + math.cos(ang + 0.17) * 6 * s, by)
            l2 = (bx - math.cos(ang + 0.17) * 6 * s + math.cos(ang) * 10 * s, by + 4 * s)
            ld.polygon([cxy(C0, *l1), cxy(C0, *tip), cxy(C0, *l2), cxy(C0, bx - 16 * s, by + 6 * s), cxy(C0, bx + 16 * s, by + 6 * s)], fill=FLAME + (235,))
            tip2 = (bx, by - 50 * s * fl)
            ld.polygon([cxy(C0, bx - 8 * s, by + 4 * s), cxy(C0, *tip2), cxy(C0, bx + 8 * s, by + 4 * s)], fill=FLAME2 + (220,))
        im.alpha_composite(L)
    if not knob:
        return
    circ(d, C0, cx + 300 * s, cy + 180 * s, 46 * s, fill=(210, 212, 220, 255))
    rr(d, C0, cx + 292 * s, cy + 140 * s, cx + 308 * s, cy + 220 * s, 6 * s, fill=(120, 124, 136, 255))


def smell(im, x, y, r, a=1.0, col=(150, 230, 140)):
    """Wavy smell lines rising."""
    L, ld = layer(im)
    for j in range(3):
        ph = (r * 0.8 + j / 3) % 1
        pts = [cxy(C0, x + (j - 1) * 60 + 18 * math.sin(u * 6 + r * 4), y - u * 220 - ph * 60) for u in [k / 12 for k in range(13)]]
        ld.line(pts, fill=col + (int(220 * a * (1 - ph)),), width=max(3, int(12 * C0[0] * SC)), joint="curve")
    im.alpha_composite(L)


def school(d, cx, cy, s, crack=0.0):
    rr(d, C0, cx - 330 * s, cy - 150 * s, cx + 330 * s, cy + 230 * s, 8, fill=(196, 150, 110, 255))
    d.polygon([cxy(C0, cx - 360 * s, cy - 150 * s), cxy(C0, cx, cy - 300 * s), cxy(C0, cx + 360 * s, cy - 150 * s)], fill=(150, 70, 60, 255))
    for row in range(2):
        for col in range(5):
            x = cx - 260 * s + col * 130 * s; y = cy - 100 * s + row * 140 * s
            rr(d, C0, x, y, x + 80 * s, y + 90 * s, 6, fill=(250, 226, 140, 255) if crack < 0.5 else (60, 50, 50, 255))
    rr(d, C0, cx - 50 * s, cy + 110 * s, cx + 50 * s, cy + 230 * s, 6, fill=(110, 70, 50, 255))
    # basement strip
    rr(d, C0, cx - 330 * s, cy + 230 * s, cx + 330 * s, cy + 330 * s, 0, fill=(80, 70, 70, 255))
    d.line([cxy(C0, cx, cy - 300 * s), cxy(C0, cx, cy - 345 * s)], fill=(230, 230, 230, 255), width=6)
    d.polygon([cxy(C0, cx, cy - 345 * s), cxy(C0, cx + 60 * s, cy - 330 * s), cxy(C0, cx, cy - 315 * s)], fill=(240, 72, 72, 255))


def gasfog(im, cx, cy, r, k, col=GASC, a0=110):
    """Gas cloud (translucent blobs) filling area, k = 0..1."""
    if k <= 0:
        return
    L, ld = layer(im)
    for i in range(14):
        ang = i * 2.4
        rad = 70 + 30 * math.sin(i * 1.7)
        x = cx + math.cos(ang) * 260 * (0.3 + 0.7 * k) + 14 * math.sin(r * 2 + i)
        y = cy + math.sin(ang) * 90 * (0.3 + 0.7 * k)
        circ(ld, C0, x, y, rad * (0.5 + 0.5 * k), fill=col + (int(a0 * k * 0.55),))
    im.alpha_composite(L)


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: burner lit, zoom-in, smell lines — big '냄새 0' hook text on top
    panel(d, BG1)
    z = 1.0 + 0.08 * ez(r / 0.6)
    burner(im, d, 540, 900, 0.95 * z, r, knob=False)
    smell(im, 540, 700, r, 0.9)
    emo(im, 860, 640, 150 + 8 * math.sin(r * 5), "👃", rot=-10)


def sMethane(r, im, d):  # 메탄: 색도 냄새도 없음
    panel(d, BG1)
    cx, cy = 540, 700
    k = ez(r / 0.5)
    for i, (dx, dy) in enumerate(((-190, -150), (190, -150), (-190, 150), (190, 150))):
        kk = ez((r - 0.15 * i) / 0.4)
        x, y = cx + dx * kk, cy + dy * kk
        d.line([cxy(C0, cx, cy), cxy(C0, x, y)], fill=(220, 224, 236, 255), width=max(4, int(16 * C0[0] * SC)))
        circ(d, C0, x, y, 62 * kk, fill=(235, 238, 245, 255))
        if kk > 0.6:
            txt(d, C0, x, y, "H", 56, INK)
    circ(d, C0, cx, cy, 105 * k, fill=(60, 64, 80, 255), outline=(220, 224, 236, 255), width=6)
    if k > 0.6:
        txt(d, C0, cx, cy, "C", 80, WHITE)
    pill(d, C0, 540, 420, "도시가스 주성분 = 메탄", 50, WHITE, INK, sc=kpop(r, 0.1))
    pill(d, C0, 330, 1040, "색 0", 64, YEL, INK, sc=kpop(r, 0.9))
    pill(d, C0, 750, 1040, "냄새 0", 64, YEL, INK, sc=kpop(r, 1.5))


def sQ(r, im, d):  # 리훅: 그럼 이 냄새는?
    panel(d, (46, 40, 76))
    burner(im, d, 540, 960, 0.75, r)
    smell(im, 540, 820, r, 1.0)
    emo(im, 540, 520, 230 * kpop(r, 0.05, .3), "🤔")
    emo(im, 790, 430, 120 * kpop(r, 0.5, .25), "❓", rot=12)


def sSchool(r, im, d):  # 진짜 이유: 1937 미국 학교
    panel(d, (52, 74, 108))
    school(d, 540, 760, 1.0 + 0.04 * r)
    pill(d, C0, 540, 400, "1937년 미국 텍사스", 54, YEL, INK, sc=kpop(r, 0.1))
    if r > 1.0:
        pill(d, C0, 540, 1170, "한 학교", 50, WHITE, INK, sc=kpop(r, 1.0))
    for i, x in enumerate((280, 410, 670, 800)):
        emo(im, x, 690, 80 * kpop(r, 2.0 + 0.2 * i, .25), "🧒")


def sLeak(r, im, d):  # 새는 가스를 아무도 못 맡음 → 폭발 → 약 300명
    t_boom = 2.2
    if r < t_boom:
        panel(d, (52, 74, 108))
        school(d, 540, 760, 1.04)
        gasfog(im, 540, 1050, r, ez(r / 1.6), col=(200, 210, 230), a0=90)
        pill(d, C0, 540, 400, "지하에 가스가 새는데", 48, WHITE, INK, sc=kpop(r, 0.1))
        emo(im, 870, 520, 120 * kpop(r, 0.6, .25), "👃")
        badge(d, C0, 930, 470, 40, RED, "x", kpop(r, 0.9, .25))
        stamp(d, C0, 540, 1170, "냄새가 없어 몰랐다", r, 1.0, RED, 50)
    else:
        q = r - t_boom
        panel(d, (90, 40, 40))
        shake = 10 * math.sin(q * 50) * max(0, 1 - q / 0.8)
        school(d, 540 + shake, 790, 1.0, crack=1.0)
        emo(im, 540, 700, 420 * kpop(q, 0.0, .3), "💥")
        if q < 0.25:
            L, ld = layer(im); rr(ld, C0, 70, 280, 1010, 1240, 70, fill=(255, 255, 255, int(230 * (1 - q / 0.25)))); im.alpha_composite(L)
        stamp(d, C0, 540, 1140, "약 300명 사망", q, 0.5, RED, 66)


def sAdd(r, im, d):  # 그 뒤로 일부러 고약한 냄새를 섞음
    panel(d, BG1)
    # pipe
    rr(d, C0, 110, 820, 970, 940, 50, fill=(170, 176, 190, 255))
    gasfog(im, 540, 880, r, 1.0, col=(230, 236, 246), a0=60)
    k = ez((r - 0.3) / 0.7)
    emo(im, 540, lerp(430, 790, k), 120, "💧")
    if r > 1.0:
        smell(im, 540, 800, r, min(1.0, (r - 1.0) / 0.4))
    pill(d, C0, 540, 400, "일부러 넣는 냄새", 54, YEL, INK, sc=kpop(r, 0.1))
    emo(im, 330, 1100, 130 * kpop(r, 1.2, .25), "🧅")
    emo(im, 540, 1100, 130 * kpop(r, 1.5, .25), "🥚")
    pill(d, C0, 780, 1100, "썩은 냄새", 46, WHITE, INK, sc=kpop(r, 1.8))


def sWarn(r, im, d):  # 그 냄새는 경고
    panel(d, (60, 44, 64))
    burner(im, d, 540, 920, 0.8, r, lit=False)
    smell(im, 540, 800, r, 1.0)
    emo(im, 540, 540, 190 * kpop(r, 0.2, .3) * (1 + 0.06 * math.sin(r * 12)), "🚨")
    rings(d, C0, 540, 540, 120, r, col=RED, spread=30)
    stamp(d, C0, 540, 1160, "가스가 샌다는 신호", r, 0.8, RED, 54)


def card(im, d, x, y, ch, label, ok, k):
    if k <= 0:
        return
    s = k
    rr(d, C0, x - 140 * s, y - 170 * s, x + 140 * s, y + 170 * s, 36 * s, fill=(250, 250, 252, 255))
    emo(im, x, y - 30 * s, 150 * s, ch)
    txt(d, C0, x, y + 110 * s, label, max(8, int(40 * s)), INK)
    badge(d, C0, x + 110 * s, y - 140 * s, 44 * s, GREEN if ok else RED, "check" if ok else "x", min(1.0, k))


def sDo(r, im, d):  # 스위치 X, 밸브 잠그기 O, 창문 열기 O
    panel(d, (40, 60, 90))
    pill(d, C0, 540, 400, "냄새 나면", 56, YEL, INK, sc=kpop(r, 0.0))
    card(im, d, 240, 800, "💡", "스위치", False, kpop(r, 0.3))
    card(im, d, 540, 800, "🔧", "밸브 잠금", True, kpop(r, 1.4))
    card(im, d, 840, 800, "🪟", "창문 열기", True, kpop(r, 2.2))


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 버너
    panel(d, BG1)
    burner(im, d, 540, 900, 0.95, r, knob=False)
    smell(im, 540, 700, r, 0.9)
    emo(im, 860, 640, 150 * kpop(r, 0.3, .25), "📲")
    emo(im, 220, 640, 150 * kpop(r, 2.4, .25), "👵")


SPOKEN = [
    "도시가스 원래 냄새는, 제로예요.",
    "주성분 메탄은, 색도 냄새도 없거든요.",
    "그럼 우리가 맡던 그 냄새는, 대체 뭘까요?",
    "진짜 이유는, 천구백삼십칠 년, 미국의 한 학교에 있어요.",
    "새는 가스를 아무도 못 맡았고, 학교가 폭발해 약 삼백 명이 숨졌어요.",
    "그 뒤로 가스에 일부러, 고약한 냄새를 섞게 됐죠.",
    "그러니까 그 냄새는, 가스가 샌다는 경고예요.",
    "냄새가 나면 스위치는 건드리지 말고, 밸브 잠그고 창문 여세요.",
    "부모님께 꼭 보내 드리세요! 팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (3, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("주성분 ", W_), ("메탄", Y_), ("은", W_)], [("색도 ", W_), ("냄새도 없어요", Y_)], sMethane),
    ("", [("그럼 우리가 맡던", W_)], [("그 냄새", Y_), ("는 뭘까요?", W_)], sQ),
    ("", [("진짜 이유는", W_)], [("1937년", Y_), (" 미국의 한 학교", W_)], sSchool),
    ("", [("새는 가스를 ", W_), ("아무도 못 맡았고", Y_)], [("폭발로 ", W_), ("약 300명", Y_), ("이 숨졌어요", W_)], sLeak),
    ("", [("그 뒤로 가스에 ", W_), ("일부러", Y_)], [("고약한 냄새", Y_), ("를 섞게 됐죠", W_)], sAdd),
    ("", [("그러니까 그 냄새는", W_)], [("가스가 샌다는 ", W_), ("경고", Y_)], sWarn),
    ("", [("스위치는 그대로", Y_)], [("밸브 잠그고 ", W_), ("창문 열기", Y_)], sDo),
    ("", [("부모님께 꼭 보내 드리세요", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)], sEnd),
]
T = (("가스 냄새", Y_), ("의 정체", W_))
Q = [[[("도시가스 원래 냄새", W_)]]]
EV = lambda s: [("pop", s[1] + 0.1, 700), ("pop", s[1] + 0.9, 800), ("pop", s[1] + 1.5, 900), ("pop", s[2] + 0.5, 1000),
                ("whoosh", s[3] + 0.05), ("pop", s[3] + 0.1, 800), ("no", s[4] + 1.2), ("thud", s[4] + 2.2, .6), ("thud", s[4] + 2.7, .4),
                ("whoosh", s[5] + 0.3), ("pop", s[5] + 1.2, 800), ("pop", s[5] + 1.5, 900), ("buzz", s[6] + 0.2), ("thud", s[6] + 0.8, .4),
                ("no", s[7] + 0.3), ("yes", s[7] + 1.4), ("yes", s[7] + 2.2), ("pop", s[8] + 0.3, 1000)]
EP = build(28, "ep28", LINES, T, Q, EV, qsize=104, qys=(1175,), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img
_cq = EP.center_q


def _center_q(im, t):  # H14: the number '0' huge on screen from frame 0
    _cq(im, t)
    if t < EP.qend:
        out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
        put(im, line_img((("0", Y_),), 420), 540, 640, out, (1 + 0.12 * (1 - ease(t / 0.25))) * (1 + 0.03 * math.sin(t * 9)))


EP.center_q = _center_q
if __name__ == "__main__":
    main(EP, "e28")
