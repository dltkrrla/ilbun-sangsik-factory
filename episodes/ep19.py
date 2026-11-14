"""19편 - 수능 날, 전국 공항이 35분 멈추는 이유 (첫 3초 포맷 H1~H6 적용 첫 편)
사실: 국토교통부 — 영어 듣기평가 13:05~13:40(전후 5분 포함 35분) 비상·긴급 제외 모든 항공기 이륙 금지,
비행 중 항공기는 3km 이상 상공 대기. 2026학년도(작년) 국제선 65·국내선 75 = 140편 조정 (헤럴드경제 2025-11-10).
2027학년도 수능 2026-11-19(목), 응시 예정 551,864명 (정책브리핑 korea.kr)."""
import math
from kit import *
from vtl import build, main

SKY = (70, 120, 190)
SKY2 = (40, 70, 130)
RUNWAY = (60, 64, 72)


def plane(im, x, y, size, heading=0.0, a=1.0):
    """heading: 0 = flying right. ✈️ glyph points up-right (45°)."""
    emo(im, x, y, size, "✈️", rot=heading - 45, a=a)


def clouds(d, t, y0=380, speed=60, a=200):
    for i, (bx, by, r) in enumerate(((180, 0, 46), (520, 60, 60), (860, -20, 50), (330, 150, 38), (720, 200, 44))):
        x = 90 + ((bx - t * speed * (1 + i % 2 * .5)) % 940)
        for dx, dr in ((-r * .8, .7), (0, 1.0), (r * .8, .75)):
            circ(d, C0, x + dx, y0 + by, r * dr, fill=(255, 255, 255, a))


def soundwaves(d, x, y, t, col=WHITE, n=3, a=255):
    for i in range(n):
        ph = (t * 1.6 + i / n) % 1
        r = 40 + ph * 110
        x0, y0 = cxy(C0, x - r, y - r); x1, y1 = cxy(C0, x + r, y + r)
        d.arc([x0, y0, x1, y1], -50, 50, fill=col + (int(a * (1 - ph)),), width=8)


# ---------------- scenes (r = seconds since the scene started) ----------------
def sHook(r, im, d):
    """H3: moving from frame 0 — a plane crosses the sky, then a red STOP slams down at 0.7s."""
    panel(d, SKY)
    clouds(d, r)
    k = min(1.0, r / 0.7)
    x = lerp(150, 470, ease(k))
    shake = 7 * math.sin(r * 40) if r > 0.7 else 0
    plane(im, x + shake, 1010, 150, heading=0)
    if r > 0.7:
        circ(d, C0, 800, 1000, 105 * kpop(r, 0.7, .22), fill=RED + (255,), outline=WHITE + (255,), width=8)
        txt(d, C0, 800, 1000, "STOP", 58 * kpop(r, 0.7, .22) + 1, WHITE)


def sExam(r, im, d):
    panel(d, (52, 62, 98))
    rr(d, C0, 160, 900, 920, 960, 10, fill=(176, 126, 88, 255))  # desk
    emo(im, 420, 760, 220 * kpop(r, 0, .25), "🎧")
    emo(im, 680, 800, 150 * kpop(r, .15, .25), "📝")
    soundwaves(d, 520, 640, r, YEL)
    pill(d, C0, 540, 420, "3교시 영어 듣기평가", 54, YEL, INK, sc=kpop(r, 0.3))
    if r > 1.2:   # H5: a new element ~every 1.5 s
        plane(im, 820, 560, 110, heading=180, a=.9)
        badge(d, C0, 820, 560, 60, RED, "x", kpop(r, 1.2, .25))


def sClock(r, im, d):
    panel(d, (40, 52, 84))
    cx, cy, R = 540, 700, 230
    circ(d, C0, cx, cy, R, fill=(250, 250, 252, 255))
    # red sector 1:05 → 1:40 (minute hand 25° → 240°)
    k = ease((r - 0.2) / 1.6)
    if k > 0:
        x0, y0 = cxy(C0, cx - R + 18, cy - R + 18); x1, y1 = cxy(C0, cx + R - 18, cy + R - 18)
        d.pieslice([x0, y0, x1, y1], -90 + 30, -90 + 30 + 210 * k, fill=(255, 107, 107, 200))
    for i in range(12):
        a = i / 12 * 2 * math.pi
        d.line([cxy(C0, cx + math.sin(a) * (R - 30), cy - math.cos(a) * (R - 30)), cxy(C0, cx + math.sin(a) * (R - 8), cy - math.cos(a) * (R - 8))], fill=INK + (255,), width=8)
    hm = math.radians(30 + 210 * k)       # minute hand
    hh = math.radians(30 + 17 * k)        # hour hand near 1
    d.line([cxy(C0, cx, cy), cxy(C0, cx + math.sin(hm) * (R - 50), cy - math.cos(hm) * (R - 50))], fill=INK + (255,), width=12)
    d.line([cxy(C0, cx, cy), cxy(C0, cx + math.sin(hh) * (R - 110), cy - math.cos(hh) * (R - 110))], fill=INK + (255,), width=16)
    circ(d, C0, cx, cy, 16, fill=INK + (255,))
    pill(d, C0, 540, 400, "오후 1:05 → 1:40", 56, WHITE, INK, sc=kpop(r, 0.1))
    if r > 1.6:
        pill(d, C0, 540, 1010, "35분", 80, YEL, INK, sc=kpop(r, 1.6, .25))


def sTakeoff(r, im, d):
    panel(d, SKY2)
    rr(d, C0, 70, 900, 1010, 1060, 0, fill=RUNWAY + (255,))
    for x in range(110, 1000, 120):
        rr(d, C0, x, 972, x + 60, 988, 3, fill=(240, 240, 240, 255))
    plane(im, 360, 860, 200, heading=0)
    badge(d, C0, 520, 720, 64, RED, "x", kpop(r, 0.3, .25))
    pill(d, C0, 360, 420, "이륙 금지", 64, RED, WHITE, sc=kpop(r, 0.2))
    if r > 1.3:
        emo(im, 790, 600, 170 * kpop(r, 1.3, .25), "🚁")
        badge(d, C0, 900, 520, 50, GREEN, "check", kpop(r, 1.5, .25))
        txt(d, C0, 790, 760, "비상·긴급만", 40, WHITE, a=255 * ease((r - 1.5) / .3))


def sHolding(r, im, d):
    panel(d, SKY)
    clouds(d, r, y0=1000, speed=30, a=160)
    cx, cy = 540, 680
    x0, y0 = cxy(C0, cx - 300, cy - 170); x1, y1 = cxy(C0, cx + 300, cy + 170)
    d.ellipse([x0, y0, x1, y1], outline=(255, 255, 255, 140), width=5)
    for i in range(3):
        a = r * 1.4 + i * 2 * math.pi / 3
        px, py = cx + math.cos(a) * 300, cy + math.sin(a) * 170
        plane(im, px, py, 120, heading=math.degrees(math.atan2(-math.cos(a) * 170, -math.sin(a) * 300)))
    d.line([cxy(C0, 130, 920), cxy(C0, 950, 920)], fill=YEL + (255,), width=6)
    txt(d, C0, 540, 970, "▲ 3km 이상", 50, YEL)
    if r > 1.0:
        pill(d, C0, 540, 400, "빙글빙글 대기 중", 52, WHITE, INK, sc=kpop(r, 1.0))


def sCount(r, im, d):
    panel(d, (40, 52, 84))
    k = ease((r - 0.1) / 1.4)
    n = int(round(140 * k))
    cols = 14
    for i in range(n):
        gx, gy = 150 + (i % cols) * 56, 520 + (i // cols) * 46
        col = (WHITE if i % 2 else (190, 205, 235)) + (255,)
        rr(d, C0, gx - 16, gy - 4, gx + 16, gy + 4, 4, fill=col)
        rr(d, C0, gx - 4, gy - 14, gx + 4, gy + 14, 3, fill=col)
    txt(d, C0, 540, 1050, f"{n}편", 120, YEL)
    pill(d, C0, 540, 420, "작년 수능 날", 52, WHITE, INK, sc=kpop(r, 0))


def sQuiet(r, im, d):
    panel(d, (44, 62, 70))
    emo(im, 540, 740, 300, "🏫")
    emo(im, 790, 520, 150 * kpop(r, 0.3, .25), "🤫")
    # noise meter going down
    k = 1 - ease((r - 0.2) / 1.2)
    rr(d, C0, 200, 980, 880, 1020, 20, fill=(255, 255, 255, 60))
    rr(d, C0, 200, 980, 200 + 680 * max(0.05, k), 1020, 20, fill=mix(GREEN, RED, k) + (255,))
    pill(d, C0, 330, 440, "올해 응시 55만 명", 46, YEL, INK, sc=kpop(r, 1.0))


def sTip(r, im, d):
    panel(d, (52, 62, 98))
    rr(d, C0, 200, 520, 880, 900, 26, fill=(250, 250, 252, 255))
    rr(d, C0, 200, 520, 880, 600, 26, fill=BLUE + (255,))
    txt(d, C0, 540, 560, "BOARDING PASS", 40, WHITE)
    txt(d, C0, 540, 680, "11/19 (목)", 64, INK)
    k = kpop(r, 0.4, .25)
    txt(d, C0, 540, 790, "13:05 ~ 13:40", 60 * k + 1, RED)
    if r > 1.2:
        badge(d, C0, 840, 520, 60, YEL, "!", kpop(r, 1.2, .25))
    emo(im, 300, 1040, 120, "⏰", rot=10 * math.sin(r * 10))


def sEnd(r, im, d):
    panel(d, SKY)
    clouds(d, r)
    plane(im, lerp(300, 820, ease(r / 2.2)), lerp(820, 480, ease(r / 2.2)), 200, heading=35)
    emo(im, 300, 1020, 140, "📚")
    rings(d, C0, 540, 700, 200, r)


SPOKEN = [
    "한국의 모든 공항이, 삼십오 분 동안 멈춰요.",
    "다음 주 목요일, 수능 영어 듣기평가 때문이에요.",
    "오후 한 시 오 분부터, 한 시 사십 분까지예요.",
    "이 시간엔 비상용 말고는, 이륙이 전부 금지되고,",
    "날고 있던 비행기는, 삼 킬로미터 위에서 빙글빙글 기다려요.",
    "작년엔 무려, 백사십 편이 시간을 바꿨대요.",
    "학생들이 듣기 한 문제 놓치지 않게, 나라 전체가 조용해지는 거죠.",
    "그날 비행기 타시는 분, 출발 시간 꼭 확인하세요!",
    "알고 있었다면, 댓글로 알려 주세요!",
]
EMOTIONS = ["surprised", "excited", "explain", "explain", "amazed", "surprised", "secret", "excited", "bright"]
BREATHS = (2, 4, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("11월 19일 수능", W_)], [("영어 듣기평가", Y_), (" 때문", W_)], sExam),
    ("", [("오후 1시 5분부터", W_)], [("1시 40분까지", Y_)], sClock),
    ("", [("비상용 말고는", W_)], [("이륙 전부 금지", Y_)], sTakeoff),
    ("", [("날던 비행기는", W_)], [("3km 위에서 대기", Y_)], sHolding),
    ("", [("작년엔 무려", W_)], [("140편", Y_), ("이 시간 조정", W_)], sCount),
    ("", [("듣기 한 문제 위해", W_)], [("나라 전체가 조용", Y_)], sQuiet),
    ("", [("그날 비행기 타면", W_)], [("출발 시간 확인!", Y_)], sTip),
    ("", [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)], sEnd),
]
T = (("수능 날 ", W_), ("공항이 멈추는", Y_), (" 이유", W_))
Q = [[[("모든", W_)], [("공항이", W_)]], [[("35분", Y_)], [("멈춘다", W_)]]]
EV = lambda s: [("whoosh", 0.05), ("thud", 0.72, .4), ("buzz", 0.75), ("pop", s[1] + .3, 800), ("no", s[1] + 1.2),
                ("click", s[2] + .2), ("ding", s[2] + 1.6, 1568), ("no", s[3] + .3), ("yes", s[3] + 1.5),
                ("whoosh", s[4] + .1), ("ding", s[5] + 1.5, 1760), ("pop", s[6] + 1.0, 900), ("pop", s[7] + .4, 1000)]
EP = build(19, "ep19", LINES, T, Q, EV, spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e19")
