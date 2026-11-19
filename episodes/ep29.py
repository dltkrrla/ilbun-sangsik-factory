"""29편 - 도어락 비밀번호, 앞뒤로 아무 숫자나 더 눌러도 열린다 (허수 기능)
주제 아레나 2026-11-19 (100개 후보 → 중복 17개 탈락 → 83강 토너먼트) 우승: 미스터리 관점 '도어락 앞뒤 아무 숫자'.
사실:
- 디지털 도어락 '허수 기능': 실제 비밀번호 앞이나 뒤에 아무 숫자를 더 눌러도 열린다. 지문이 키패드 전체에 고르게 남아
  지문 자국으로 번호를 짐작하기 어렵게 하는 기능 (위키트리 https://www.wikitree.co.kr/articles/1136517)
- 허수 개수·방식은 제조사마다 다름: 아이레보·에버넷 제한 없음, 웅진 최대 10자리, 삼성은 불 켜진 숫자 2개를 먼저 누르는 방식
  (에누리 구매가이드 https://enuri.com/knowcom/detail.jsp?kbno=281516 · 삼성 뉴스룸 https://news.samsung.com/kr/3342)
- 허수 지원 여부와 방식은 제품마다 다르므로 설명서 확인 (miso.kr https://miso.kr/blog/thread/도어락-허수-비밀번호-꿀팁)
- '경우의 수 24': 서로 다른 숫자 4개가 정해지면 순서는 4×3×2×1 = 24가지 (계산)
바꿀 것 1개(플레이북 H14 유지): 첫 문장 = 숫자 하나가 든 단정형("경우의 수는 딱 스물네 개"), 0초 화면에 큰 '24'.
평면 그림(26~28편과 같은 방식), 6초 리훅, 끝 장면 = 첫 장면(루프), 첫 장면은 가운데 키패드 하나(H15)."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
WOOD = (120, 84, 60)
WOOD2 = (104, 72, 52)
BODY = (28, 30, 38)
KEY = (52, 56, 70)
KEYLIT = (90, 170, 255)
SMUDGE = (235, 225, 190)
PW = "1479"
KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "*", "0", "#"]


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def layer(im):
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); return L, ImageDraw.Draw(L)


def door(d):
    """Wooden front door filling the scene, with vertical grain panels."""
    rr(d, C0, 80, 250, 1000, 1300, 30, fill=WOOD + (255,))
    for i in range(6):
        x = 150 + i * 150
        d.line([cxy(C0, x, 270), cxy(C0, x, 1280)], fill=WOOD2 + (255,), width=max(2, int(6 * C0[0] * SC)))


def key_xy(cx, cy, s, k):
    i = KEYS.index(k)
    row, col = divmod(i, 3)
    return cx + (col - 1) * 150 * s, cy - 120 * s + (row - 1.5) * 140 * s


def keypad(im, d, cx, cy, s, r, smudge=None, lit=(), press=None, handle=True):
    """Door-lock keypad: dark body, 3x4 keys, optional finger-grease smudges (dict key->alpha 0..1) and lit keys."""
    smudge = smudge or {}
    rr(d, C0, cx - 270 * s, cy - 480 * s, cx + 270 * s, cy + 420 * s, 70 * s, fill=(60, 62, 72, 255))
    rr(d, C0, cx - 250 * s, cy - 460 * s, cx + 250 * s, cy + 400 * s, 60 * s, fill=BODY + (255,))
    for k in KEYS:
        x, y = key_xy(cx, cy, s, k)
        on = k in lit
        rr(d, C0, x - 60 * s, y - 55 * s, x + 60 * s, y + 55 * s, 26 * s, fill=(KEYLIT if on else KEY) + (255,))
        txt(d, C0, x, y, k, max(8, int(58 * s)), INK if on else WHITE)
    if smudge:
        L, ld = layer(im)
        for k, a in smudge.items():
            if a <= 0:
                continue
            x, y = key_xy(cx, cy, s, k)
            for j in range(3):  # oily, slightly offset ovals
                ox, oy = 14 * math.sin(j * 2.1 + KEYS.index(k)) * s, 10 * math.cos(j * 1.7 + KEYS.index(k)) * s
                circ(ld, C0, x + ox, y + oy, (40 - 8 * j) * s, fill=SMUDGE + (int(95 * a),))
        im.alpha_composite(L)
        for k, a in smudge.items():  # glint on the greasy keys
            if a > 0.6:
                x, y = key_xy(cx, cy, s, k)
                emo(im, x + 38 * s, y - 34 * s, 46 * s * (0.8 + 0.2 * math.sin(r * 6 + KEYS.index(k))), "✨")
    if press is not None:
        x, y = key_xy(cx, cy, s, press)
        emo(im, x + 40 * s, y + 70 * s, 150 * s, "👆")
    if handle:
        rr(d, C0, cx - 60 * s, cy + 440 * s, cx + 60 * s, cy + 620 * s, 30 * s, fill=(170, 174, 186, 255))


def display(d, x, y, digits, size=72):
    """Row of typed digits; real password digits yellow, extra (허수) digits grey."""
    n = len(digits)
    w = size * 0.9
    rr(d, C0, x - (n * w) / 2 - 30, y - size * 0.8, x + (n * w) / 2 + 30, y + size * 0.8, 30, fill=(250, 250, 252, 255))
    for i, (ch, real) in enumerate(digits):
        txt(d, C0, x - (n - 1) * w / 2 + i * w, y, ch, size, (230, 160, 0) if real else (150, 150, 160))


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: keypad with 4 greasy keys, slow zoom, magnifier sweeping — big '24' on top
    panel(d, BG1)
    door(d)
    z = 0.64 * (1.0 + 0.08 * ez(r / 0.6))
    keypad(im, d, 540, 960, z, r, smudge={k: 1.0 for k in PW}, handle=False)
    emo(im, 540 + 130 * math.sin(r * 2.2), 900 + 50 * math.cos(r * 2.2), 140, "🔍")
    if r > 2.6:  # H5: second beat inside the long first line — rings on the 4 greasy keys + a thief peeking
        for k in PW:
            x, y = key_xy(540, 960, z, k)
            rings(d, C0, x, y, 40, r - 2.6, col=RED, spread=16)
        emo(im, 900, 760, 150 * kpop(r, 2.7, .3), "🕵️")


def sGrease(r, im, d):  # 자주 누른 버튼에만 손 기름 → 1.6초부터 24가지 순서
    if r > 1.6:
        return sCount(r - 1.6, im, d)
    panel(d, BG1)
    door(d)
    keypad(im, d, 540, 880, 0.9, r, smudge={k: ez((r - 0.3 * i) / 0.4) for i, k in enumerate(PW)}, handle=False)
    pill(d, C0, 540, 420, "자주 누른 버튼만 반질반질", 48, YEL, INK, sc=kpop(r, 0.1))


def sCount(r, im, d):  # 4개 숫자 → 24가지 순서
    panel(d, (46, 40, 76))
    combos = ["1479", "1497", "1749", "1794", "4179", "4719", "7149", "9741", "7914"]
    for i, c in enumerate(combos):
        row, col = divmod(i, 3)
        pill(d, C0, 230 + col * 310, 480 + row * 160, c, 60, WHITE, INK, sc=kpop(r, 0.05 * i))
    if r > 0.6:
        stamp(d, C0, 540, 1000, "딱 24가지", r, 0.6, RED, 80)
    emo(im, 540, 1150, 120 * kpop(r, 0.9, .25), "😱")


def sHidden(r, im, d):  # 리훅: 숨은 기능
    panel(d, (40, 50, 84))
    door(d)
    keypad(im, d, 540, 980, 0.62, r, handle=False)
    emo(im, 540, 520, 210 * kpop(r, 0.05, .3), "🤫")
    rings(d, C0, 540, 520, 120, r, col=YEL, spread=30)
    if r > 0.8:
        pill(d, C0, 540, 1110, "숨은 기능", 64, YEL, INK, sc=kpop(r, 0.8))


SEQ = [("8", False), ("2", False), ("1", True), ("4", True), ("7", True), ("9", True), ("5", False)]


def sTrick(r, im, d):  # 앞뒤로 아무 숫자 섞어 누르기 → 열림
    panel(d, BG1)
    door(d)
    step = 0.32
    n = min(len(SEQ), int(max(0.0, r - 0.2) / step) + 1) if r > 0.2 else 0
    cur = SEQ[n - 1][0] if 0 < n and r < 0.2 + len(SEQ) * step else None
    keypad(im, d, 540, 960, 0.72, r, lit=(cur,) if cur else (), press=cur, handle=True)
    if n:
        display(d, 540, 380, SEQ[:n], 76)
    t_open = 0.3 + len(SEQ) * step
    if r > t_open:
        emo(im, 880, 640, 170 * kpop(r, t_open, .3), "🔓")
        badge(d, C0, 200, 640, 60, GREEN, "check", kpop(r, t_open + 0.1, .25))


def sName(r, im, d):  # 이름하여 허수 기능
    panel(d, (52, 60, 100))
    display(d, 540, 560, SEQ, 92)
    k = ez((r - 0.3) / 0.4)
    for i, (ch, real) in enumerate(SEQ):
        if not real:
            x = 540 - (len(SEQ) - 1) * 92 * 0.9 / 2 + i * 92 * 0.9
            emo(im, x, 450 - 30 * k, 70 * k, "🎭")
    pill(d, C0, 540, 860, "허수 = 가짜 숫자", 70, YEL, INK, sc=kpop(r, 0.6))
    pill(d, C0, 540, 1050, "앞뒤 아무 숫자 OK", 50, WHITE, INK, sc=kpop(r, 1.2))


def sSpread(r, im, d):  # 매번 섞으면 자국이 전체로 퍼짐
    panel(d, BG1)
    door(d)
    sm = {k: (1.0 if k in PW else ez((r - 0.25 - 0.12 * i) / 0.35)) for i, k in enumerate(KEYS)}
    keypad(im, d, 540, 880, 0.9, r, smudge=sm, handle=False)
    if r > 1.6:
        stamp(d, C0, 540, 410, "어디가 진짜?", r, 1.6, RED, 60)


def sPeek(r, im, d):  # 뒤에서 훔쳐봐도 모름
    panel(d, (46, 40, 76))
    door(d)
    j = min(len(SEQ) - 1, int(r / 0.3) % len(SEQ))
    keypad(im, d, 600, 960, 0.7, r, lit=(SEQ[j][0],), press=SEQ[j][0], handle=False)
    emo(im, 210, 600 + 10 * math.sin(r * 4), 210 * kpop(r, 0.0, .3), "👀")
    emo(im, 300, 420, 120 * kpop(r, 1.0, .25), "❓", rot=-10)
    emo(im, 160, 470, 90 * kpop(r, 1.3, .25), "❓", rot=12)


def sCheck(r, im, d):  # 제품마다 방식이 다름 → 우리 집 도어락으로 확인
    panel(d, (40, 60, 90))
    pill(d, C0, 540, 420, "제품마다 방식이 달라요", 52, YEL, INK, sc=kpop(r, 0.0))
    keypad(im, d, 540, 900, 0.7, r, lit=("3", "8") if (r * 2) % 1 < 0.6 else (), handle=False)
    emo(im, 860, 620, 160 * kpop(r, 0.6, .3), "📖")
    pill(d, C0, 540, 1150, "설명서 확인", 50, WHITE, INK, sc=kpop(r, 1.2))


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 키패드
    panel(d, BG1)
    door(d)
    keypad(im, d, 540, 960, 0.64, r, smudge={k: 1.0 for k in PW}, handle=False)
    emo(im, 860, 560, 150 * kpop(r, 0.3, .25), "📲")
    emo(im, 220, 560, 150 * kpop(r, 2.0, .25), "🏠")


SPOKEN = [
    "도어락 비밀번호 네 자리, 지문 자국만 보면 경우의 수는 딱 스물네 개예요.",
    "자주 누른 버튼에만, 손 기름이 반질반질 남거든요.",
    "그런데 도어락엔, 이걸 막는 숨은 기능이 있어요.",
    "진짜 비밀번호 앞이나 뒤에, 아무 숫자를 더 눌러도 문이 열려요.",
    "이름하여, 허수 기능이에요.",
    "매번 다른 숫자를 섞으면, 자국이 버튼 전체에 퍼지죠.",
    "뒤에서 훔쳐보는 사람도, 진짜 번호를 못 알아봐요.",
    "방식은 제품마다 달라서, 설명서를 꼭 확인해 보세요.",
    "가족에게 꼭 알려 주세요! 팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (2, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("자주 누른 버튼에만", W_)], [("손 기름", Y_), ("이 반질반질", W_)], sGrease),
    ("", [("그런데 도어락엔", W_)], [("숨은 기능", Y_), ("이 있어요", W_)], sHidden),
    ("", [("비밀번호 ", W_), ("앞이나 뒤에", Y_)], [("아무 숫자", Y_), ("를 더 눌러도 열려요", W_)], sTrick),
    ("", [("이름하여", W_)], [("허수 기능", Y_)], sName),
    ("", [("매번 다른 숫자를 섞으면", W_)], [("자국이 ", W_), ("전체에 퍼져요", Y_)], sSpread),
    ("", [("뒤에서 훔쳐봐도", W_)], [("진짜 번호", Y_), ("를 몰라요", W_)], sPeek),
    ("", [("방식은 ", W_), ("제품마다 달라요", Y_)], [("설명서", Y_), ("를 확인하세요", W_)], sCheck),
    ("", [("가족에게 꼭 알려 주세요", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)], sEnd),
]
T = (("도어락", Y_), (" 숨은 기능", W_))
Q = [[[("지문 자국 4개", W_)]]]
EV = lambda s: [("pop", s[1] + 0.3, 700), ("pop", s[1] + 0.6, 800), ("pop", s[1] + 0.9, 900), ("pop", s[1] + 1.2, 1000),
                ("whoosh", s[2] + 0.05), ("pop", s[2] + 0.8, 900),
                ("pop", s[3] + 0.25, 600), ("pop", s[3] + 0.57, 650), ("pop", s[3] + 0.89, 900), ("pop", s[3] + 1.21, 950),
                ("pop", s[3] + 1.53, 1000), ("pop", s[3] + 1.85, 1050), ("pop", s[3] + 2.17, 700), ("yes", s[3] + 2.55),
                ("whoosh", s[4] + 0.05), ("pop", s[4] + 0.6, 900), ("pop", s[5] + 0.4, 800), ("thud", s[5] + 1.6, .5),
                ("no", s[6] + 1.0), ("pop", s[7] + 0.1, 800), ("pop", s[7] + 1.2, 900), ("pop", s[8] + 0.3, 1000)]
EP = build(29, "ep29", LINES, T, Q, EV, qsize=104, qys=(1175,), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img
_cq = EP.center_q


def _center_q(im, t):  # H14: the number '24' huge on screen from frame 0
    _cq(im, t)
    if t < EP.qend:
        out = 1 - ease((t - (EP.qend - 0.2)) / 0.2)
        put(im, line_img((("24", Y_),), 280), 540, 440, out, (1 + 0.12 * (1 - ease(t / 0.25))) * (1 + 0.03 * math.sin(t * 9)))


EP.center_q = _center_q
if __name__ == "__main__":
    main(EP, "e29")
