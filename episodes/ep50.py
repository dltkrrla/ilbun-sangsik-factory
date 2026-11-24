"""50편 - 버너보다 큰 불판, 가스통이 터질 수 있어요 (휴대용 가스레인지 과대 불판 → 복사열이 부탄캔을 달굼 → 압력 상승 → 파열)
주제 아레나 2026-11-24 (100개, 10관점 서브에이전트) 우승: '버너보다 큰 불판 부탄캔 폭발'(과학, 4기준 5·5·5·5).
결승 상대 '변기 뚜껑 칫솔'(15), 3강 '드라이기 선 칭칭 감기'(20, 의외성·후킹 동률 → 앞 대진). 8강 이상은 docs/ARENA.md 참고.
사실:
- 불판 받침대보다 큰 조리기구 사용 금지: 복사열로 부탄캔 내부압력이 올라 파열할 수 있음 · 휴대용 가스레인지 쌓아 보관 금지
  (한국가스안전공사, 데일리안 2021-04-21 https://m.dailian.co.kr/news/view/984290 ·
  뉴데일리 2022-05-04 https://biz.newdaily.co.kr/site/data/html/2022/05/04/2022050400163.amp.html)
- 최근 5년(2012~2016) 휴대용 부탄캔 사고 100건, 사망 8명·부상 133명 · 원인 1위 화기 근처 부탄캔 보관 24건,
  과대 불판·호일 11건 · 가스레인지를 나란히 붙여 쓰는 행위도 매우 위험 (국민안전처, 서울신문 2017-04-21
  https://m.go.seoul.co.kr/news/2017/04/21/20170421012018)
- 휴대용 가스레인지 크기보다 큰 조리도구 사용 금지 · 뜨거운 물체 주변에 부탄가스 두지 않기 · 다 쓴 통은 환기 잘 되는
  바깥에서 노즐을 눌러 비운 뒤 지정 장소에 버리기 (구멍 뚫다 폭발 사고도 있음) (소방청, 정책브리핑 2023-12-13
  https://www.korea.kr/news/policyNewsView.do?newsId=148923719)
- 과대 불판 연구: 캔 바닥 50℃ 이하에서 안전 작동 (한국연소학회 2014 https://koreascience.or.kr/article/CFKO201431751939275.page)
그대로: 평면 그림 · steady 목소리 · 위험 장면 + 결과형 첫 문장(H19) · 첫 장면 가운데 버너 하나(H15) · 끝 = 첫 장면(H13) ·
마지막 '부모님께'(L10) · 2.4초에 쉬운 결과어 첫 보상(H18 유지: "가스통을 달구거든요").
새로(사용자 결정 11/24, H20): 0초부터 화면 가운데 큰 두 줄 제목 = 첫 문장, 단어마다 팡, 여는 화면을 어둡게 깔지 않음."""
import math
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG1 = (34, 40, 70)
STEEL = (200, 205, 215)
DARK = (60, 64, 78)
PAN = (70, 72, 80)
CAN = (235, 235, 240)
FLAME = (90, 170, 255)
HOT = (255, 90, 60)
ORG = (255, 160, 60)


def ez(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


def lw(v):
    return max(2, int(v * C0[0] * SC))


def poly(d, pts, fill):
    d.polygon([tuple(cxy(C0, x, y)) for x, y in pts], fill=fill)


def line(d, pts, col, w):
    d.line([tuple(cxy(C0, x, y)) for x, y in pts], fill=col, width=lw(w))


def gascan(d, cx, cy, s=1.0, heat=0.0, bulge=0.0, lying=True):
    """Butane can. heat 0..1 turns it red; bulge widens the middle."""
    col = tuple(int(CAN[i] + (HOT[i] - CAN[i]) * heat) for i in range(3))
    if lying:
        L, R = 150 * s, (52 + 18 * bulge) * s
        rr(d, C0, cx - L, cy - R, cx + L, cy + R, R * 0.6, fill=col + (255,))
        rr(d, C0, cx - L * 0.35, cy - R, cx + L * 0.35, cy + R, 6 * s, fill=(255, 120, 80, 255) if heat < .5 else (200, 40, 30, 255))
        rr(d, C0, cx - L - 26 * s, cy - 16 * s, cx - L + 4 * s, cy + 16 * s, 6 * s, fill=(180, 180, 190, 255))
    else:
        H_, R = 190 * s, (75 + 22 * bulge) * s
        rr(d, C0, cx - R, cy - H_, cx + R, cy + H_, 24 * s, fill=col + (255,))
        rr(d, C0, cx - R, cy - H_ * 0.35, cx + R, cy + H_ * 0.35, 6 * s, fill=(255, 120, 80, 255) if heat < .5 else (200, 40, 30, 255))
        rr(d, C0, cx - 22 * s, cy - H_ - 34 * s, cx + 22 * s, cy - H_ + 4 * s, 6 * s, fill=(180, 180, 190, 255))
        txt(d, C0, cx, cy, "부탄", max(8, int(40 * s)), WHITE)


def burner(d, cx, cy, s=1.0, t=0.0, flame=True, heat=0.0, pan=0.0):
    """Portable gas stove seen from the front. Can bay on the right. pan 0 = none, 1 = small, >1 = oversized grill."""
    # body
    rr(d, C0, cx - 260 * s, cy - 40 * s, cx + 260 * s, cy + 110 * s, 22 * s, fill=STEEL + (255,))
    rr(d, C0, cx + 90 * s, cy - 20 * s, cx + 245 * s, cy + 92 * s, 14 * s, fill=(170, 175, 188, 255))   # can bay lid
    gascan(d, cx + 168 * s, cy + 36 * s, 0.42 * s, heat)
    circ(d, C0, cx - 175 * s, cy + 40 * s, 34 * s, fill=DARK + (255,))                                 # knob
    line(d, [(cx - 175 * s, cy + 40 * s), (cx - 175 * s + 26 * s * math.cos(-1.0), cy + 40 * s + 26 * s * math.sin(-1.0))], WHITE, 8 * s)
    # grate (받침대)
    rr(d, C0, cx - 150 * s, cy - 62 * s, cx + 150 * s, cy - 40 * s, 8 * s, fill=DARK + (255,))
    # flames
    if flame:
        for i in range(7):
            x = cx + (-90 + i * 30) * s
            h = (46 + 14 * math.sin(t * 17 + i * 1.7)) * s
            poly(d, [(x - 11 * s, cy - 62 * s), (x, cy - 62 * s - h), (x + 11 * s, cy - 62 * s)], FLAME + (230,))
    if pan > 0:
        w = 130 * s * pan
        rr(d, C0, cx - w, cy - 112 * s, cx + w, cy - 66 * s, 22 * s, fill=PAN + (255,))
        rr(d, C0, cx - w + 18 * s, cy - 104 * s, cx + w - 18 * s, cy - 92 * s, 6 * s, fill=(110, 112, 122, 255))
        rr(d, C0, cx - w - 40 * s, cy - 100 * s, cx - w + 4 * s, cy - 84 * s, 6 * s, fill=PAN + (255,))
        rr(d, C0, cx + w - 4 * s, cy - 100 * s, cx + w + 40 * s, cy - 84 * s, 6 * s, fill=PAN + (255,))


def heatwaves(d, x0, x1, y0, y1, r, a=200, col=HOT):
    """Wavy red heat lines travelling from y0 to y1."""
    for i in range(4):
        x = x0 + (x1 - x0) * i / 3
        ph = (r * 1.4 + i * 0.25) % 1.0
        pts = []
        for k in range(9):
            yy = y0 + (y1 - y0) * k / 8
            pts.append((x + 14 * math.sin(k * 1.3 + r * 9 + i), yy))
        line(d, pts, col + (int(a * (0.4 + 0.6 * (1 - ph))),), 9)
        yy = y0 + (y1 - y0) * ph
        poly(d, [(x - 18, yy - 10), (x + 18, yy - 10), (x, yy + 20)], col + (a,))


def gauge(d, cx, cy, v, label="압력"):
    circ(d, C0, cx, cy, 120, fill=(250, 250, 252, 255))
    for k in range(5):
        a0 = math.pi * (1 - k / 4)
        line(d, [(cx + 95 * math.cos(a0), cy - 95 * math.sin(a0)), (cx + 110 * math.cos(a0), cy - 110 * math.sin(a0))], INK, 6)
    a = math.pi * (1 - v)
    line(d, [(cx, cy), (cx + 90 * math.cos(a), cy - 90 * math.sin(a))], RED if v > .6 else INK, 10)
    circ(d, C0, cx, cy, 14, fill=INK + (255,))
    txt(d, C0, cx, cy + 60, label, 36, INK)


# ---------------- scenes ----------------
def sHook(r, im, d):  # 0 s: one burner, oversized grill pan, flames flicker, slow push-in; can glows faintly (no dark overlay)
    panel(d, BG1)
    z = 1.0 + 0.12 * ez(r / 2.4)
    burner(d, 540, 1000, 1.3 * z, r, heat=0.35 * ez(r / 2.2), pan=2.05)
    for k in range(4):  # faint heat shimmer under the overhanging grill edges
        ph = (r * 1.2 + k / 4) % 1.0
        x = (250 if k % 2 else 830) + 10 * math.sin(r * 7 + k)
        circ(d, C0, x, 900 + ph * 120, 10 + 8 * ph, fill=(255, 120, 80, int(150 * (1 - ph))))
    if r > 1.0:
        emo(im, 540, 840 - 8 * math.sin(r * 6), 110 * kpop(r, 1.0, .25), "🥩")


def sHeat(r, im, d):  # 큰 불판 열이 아래로 내려와, 가스통을 달구거든요
    panel(d, (46, 40, 76))
    heat = ez((r - 0.3) / 1.4)
    burner(d, 540, 960, 1.3, r, heat=heat, pan=2.05)
    heatwaves(d, 680, 860, 820, 960, r)
    if r > 0.5:
        pill(d, C0, 540, 430, "열이 아래로", 60, WHITE, INK, sc=kpop(r, 0.5))
    if r > 1.2:
        rings(d, C0, 758, 1007, 80, r - 1.2, col=HOT, spread=40)
        stamp(d, C0, 540, 1095, "가스통이 뜨거워요", r, 1.3, RED, 56)


def sPress(r, im, d):  # 가스통이 뜨거워지면, 안에서 압력이 쑥 올라가요 (6 s 리훅: 같은 가스통 안)
    panel(d, BG1)
    v = ez((r - 0.2) / 1.6)
    shake = 6 * v * math.sin(r * 60)
    gascan(d, 360 + shake, 820, 1.25, heat=0.4 + 0.6 * v, bulge=v, lying=False)
    for i in range(8):  # gas molecules bouncing faster inside
        ang = i * 0.8 + r * (3 + 9 * v)
        circ(d, C0, 360 + 55 * math.cos(ang * 1.3 + i), 820 + 150 * math.sin(ang + i), 13, fill=(255, 255, 255, 220))
    gauge(d, 800, 820, 0.1 + 0.85 * v)
    if r > 0.3:
        pill(d, C0, 540, 430, "압력 쑥", 76, YEL, INK, sc=kpop(r, 0.3, .35))
    if r > 1.7:
        stamp(d, C0, 540, 1095, "펑!", r, 1.7, RED, 80)


def sStats(r, im, d):  # 5년 동안 부탄캔 사고 100건, 8명이 숨졌어요
    panel(d, (52, 44, 84))
    pill(d, C0, 540, 410, "부탄캔 사고 5년 (2012~2016)", 46, WHITE, INK, sc=kpop(r, 0.05))
    n = min(100, int(ez(r / 1.0) * 100))
    for i in range(n):  # 10x10 grid of flame dots
        x = 270 + (i % 10) * 60; y = 540 + (i // 10) * 50
        circ(d, C0, x, y, 18, fill=ORG + (255,))
    pill(d, C0, 540, 1100, f"{max(n, 1)}건", 90, YEL, INK, sc=kpop(r, 0.1, .35))
    if r > 1.3:
        pill(d, C0, 830, 1100, "8명 사망", 56, RED, WHITE, sc=kpop(r, 1.3, .35))


def sNear(r, im, d):  # 원인 1위는, 불 옆에 둔 여분 가스통이에요
    panel(d, BG1)
    burner(d, 470, 900, 1.0, r, pan=1.0)
    k = kpop(r, 0.2, .3)
    if k > 0:
        gascan(d, 880, 830, 0.75 * k, heat=ez((r - 0.6) / 1.0), lying=False)
        heatwaves(d, 700, 760, 800, 860, r, a=170)
    if r > 0.1:
        pill(d, C0, 540, 430, "원인 1위", 70, YEL, INK, sc=kpop(r, 0.1, .35))
    if r > 1.2:
        badge(d, C0, 880, 620, 56, RED, "x", min(1.0, kpop(r, 1.2)))
        pill(d, C0, 540, 1095, "불 옆에 둔 가스통", 54, WHITE, INK, sc=kpop(r, 1.3))


def sTwo(r, im, d):  # 버너 두 대를 붙여 쓰는 것도, 똑같이 위험해요
    panel(d, (46, 40, 76))
    k = ez(r / 0.6)
    burner(d, 300 + 40 * k, 900, 0.8, r, pan=1.0)
    burner(d, 780 - 40 * k, 900, 0.8, r + 0.5, pan=1.0)
    if r > 0.6:
        heatwaves(d, 520, 560, 780, 900, r, a=180)
        pill(d, C0, 540, 430, "나란히 붙이기", 64, WHITE, INK, sc=kpop(r, 0.6))
    if r > 1.3:
        badge(d, C0, 540, 620, 60, RED, "x", min(1.0, kpop(r, 1.3)))


def sRule(r, im, d):  # 불판은 받침대보다 작게, 가스통은 불에서 멀리
    panel(d, BG1)
    if r < 1.1:
        burner(d, 540, 940, 1.3, r, pan=2.05)
        badge(d, C0, 860, 620, 60, RED, "x", min(1.0, kpop(r, 0.15)))
        pill(d, C0, 540, 430, "받침대보다 큰 불판", 56, WHITE, INK, sc=kpop(r, 0.05))
    else:
        burner(d, 540, 940, 1.3, r, pan=1.0)
        badge(d, C0, 860, 620, 60, GREEN, "check", min(1.0, kpop(r, 1.15)))
        pill(d, C0, 540, 430, "받침대보다 작게", 62, YEL, INK, sc=kpop(r, 1.1, .35))
        if r > 1.8:
            emo(im, 170, 1140, 100 * kpop(r, 1.8, .25), "🥫")
            pill(d, C0, 600, 1095, "가스통은 멀리", 54, WHITE, INK, sc=kpop(r, 1.9))


def sEmpty(r, im, d):  # 다 쓴 통은 바깥에서 노즐을 눌러, 가스를 다 빼고 버리세요
    panel(d, (40, 50, 84))
    emo(im, 830, 470, 120 * kpop(r, 0.05, .3), "🌳")
    gascan(d, 470, 860, 1.0, lying=False)
    press = abs(math.sin(r * 3)) if r > 0.6 else 0
    emo(im, 470, 600 - 20 * press, 130 * kpop(r, 0.4, .25), "👇")
    if r > 0.7:
        for i in range(5):
            ph = (r * 1.3 + i / 5) % 1.0
            circ(d, C0, 520 + ph * 260, 640 - ph * 120 + 20 * math.sin(i), 16 + 30 * ph, fill=(220, 230, 245, int(160 * (1 - ph))))
    if r > 1.4:
        pill(d, C0, 540, 1095, "바깥에서 다 빼고 버리기", 52, YEL, INK, sc=kpop(r, 1.4))


def sShare(r, im, d):  # 연말 모임 전에, 부모님께 꼭 보내 드리세요
    panel(d, (46, 40, 76))
    emo(im, 380, 780, 220 * kpop(r, 0.1, .3), "👴")
    emo(im, 700, 780, 220 * kpop(r, 0.3, .3), "👵")
    if r > 0.7:
        emo(im, 860, 450, 140 * kpop(r, 0.7, .3), "📲")
        rings(d, C0, 860, 450, 70, r - 0.7, col=YEL, spread=40)
    if r > 1.1:
        pill(d, C0, 540, 1100, "부모님께 보내기", 60, YEL, INK, sc=kpop(r, 1.1))


def sEnd(r, im, d):  # 루프: 첫 장면과 같은 버너 + 큰 불판
    panel(d, BG1)
    burner(d, 540, 930, 1.3, r, heat=0.35, pan=2.05)
    emo(im, 540, 770, 110, "🥩")
    emo(im, 840, 420, 120 * kpop(r, 0.5, .25), "🔔")


SPOKEN = [
    "버너보다 큰 불판, 가스통이 터질 수 있어요.",
    "불판 열이 아래로 내려와, 가스통을 달구거든요.",
    "가스통이 뜨거워지면, 안에서 압력이 쑥 올라가요.",
    "실제로 오 년 동안 부탄캔 사고 백 건, 여덟 명이 숨졌어요.",
    "원인 일위는, 불 옆에 둔 여분 가스통이에요.",
    "버너 두 대를 붙여 쓰는 것도, 똑같이 위험해요.",
    "불판은 받침대보다 작게, 가스통은 불에서 멀리.",
    "다 쓴 통은 바깥에서 노즐을 눌러, 가스를 다 빼고 버리세요.",
    "연말 모임 전에, 부모님께 꼭 보내 드리세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 10
BREATHS = (3, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("불판 열이 ", W_), ("아래로", Y_)], [("가스통을 ", W_), ("달구거든요", Y_)], sHeat),
    ("", [("가스통이 뜨거워지면", W_)], [("압력이 ", W_), ("쑥", Y_)], sPress),
    ("", [("5년", Y_), ("간 부탄캔 사고 ", W_), ("100건", Y_)], [("8명", Y_), ("이 숨졌어요", W_)], sStats),
    ("", [("원인 ", W_), ("1위", Y_), ("는", W_)], [("불 옆에 둔 ", W_), ("여분 가스통", Y_)], sNear),
    ("", [("버너 ", W_), ("두 대", Y_), (" 붙여 쓰기도", W_)], [("똑같이 ", W_), ("위험해요", Y_)], sTwo),
    ("", [("불판은 ", W_), ("받침대보다 작게", Y_)], [("가스통은 ", W_), ("불에서 멀리", Y_)], sRule),
    ("", [("다 쓴 통은 ", W_), ("바깥에서", Y_)], [("가스를 ", W_), ("다 빼고", Y_), (" 버리기", W_)], sEmpty),
    ("", [("연말 모임 전에", W_)], [("부모님께 ", W_), ("보내 드리세요", Y_)], sShare),
    ("", [("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드려요", W_)], sEnd),
]
T = (("버너보다 큰 불판,", W_), (" 가스통이 터질 수 있어요", Y_))
Q = [[[("버너보다", W_)], [("큰 불판", Y_)]], [[("가스통이", W_)], [("터질 수", Y_)], [("있어요", W_)]]]
EV = lambda s: [("pop", s[0] + 0.05, 700), ("pop", s[0] + 1.2, 900),
                ("whoosh", s[1] + 0.05), ("pop", s[1] + 0.5, 900), ("thud", s[1] + 1.3, .5),
                ("pop", s[2] + 0.3, 1000), ("buzz", s[2] + 1.2), ("thud", s[2] + 1.7, .7),
                ("pop", s[3] + 0.1, 800), ("pop", s[3] + 1.0, 1100), ("thud", s[3] + 1.3, .4),
                ("pop", s[4] + 0.1, 900), ("pop", s[4] + 0.2, 700), ("no", s[4] + 1.2), ("pop", s[4] + 1.3, 800),
                ("whoosh", s[5] + 0.3), ("pop", s[5] + 0.6, 900), ("no", s[5] + 1.3),
                ("no", s[6] + 0.15), ("whoosh", s[6] + 1.05), ("yes", s[6] + 1.15), ("pop", s[6] + 1.9, 800),
                ("pop", s[7] + 0.4, 800), ("whoosh", s[7] + 0.8), ("pop", s[7] + 1.4, 1000),
                ("pop", s[8] + 0.1, 800), ("pop", s[8] + 0.7, 1000), ("yes", s[8] + 1.1),
                ("pop", s[9] + 0.5, 1000)]
EP = build(50, "ep50", LINES, T, Q, EV, qsize=112, qys=(585, 735), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
from sangsik2 import put, line_img, F


def _center_title(im, t):
    """H20 (사용자 결정 11/24): 0초부터 화면 가운데 큰 두 줄 제목 = 첫 문장. 흰 글자 + 강조 노랑, 두꺼운 테두리,
    단어마다 팡(강조 단어에 가장 크게, H17). 여는 화면을 어둡게 깔지 않는다(H18). engine/flat/center_title.py와 같은 방식."""
    if t >= EP.qend:
        return
    a_out = 1 - ease((t - (EP.qend - 0.18)) / 0.18)
    rows, ys, size = EP.qhook
    tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size)
    hits = [-0.2, 0.3, 0.95, 1.25, 1.5]
    idx = 0
    for words, cy in zip(rows, ys):
        ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) for w in words]
        sp = size * 0.24; total = sum(ws) + sp * (len(ws) - 1)
        scf = min(1.0, 1000 / total); x = 540 - total * scf / 2
        for w, ww in zip(words, ws):
            h = hits[min(idx, len(hits) - 1)]; idx += 1
            lt = t - h
            strong = any(c == Y_ for _, c in w)
            if lt >= 0:
                sc = scf * (1 + (0.75 if strong else 0.3) * (1 - ease(lt / 0.17)))
                if strong:
                    sc *= 1 + 0.04 * math.sin(t * 9)
                put(im, line_img(tuple(w), size), x + ww * scf / 2, cy, ease(lt / 0.07) * a_out, sc)
            x += (ww + sp) * scf


EP.center_q = _center_title
if __name__ == "__main__":
    main(EP, "e50")
