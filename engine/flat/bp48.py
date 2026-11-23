"""48편 대중교통비 환급(모두의 카드) 설계도 모션그래픽 4장면.
send: 가족 단톡방에 영상 보내기 / calc: 월 7만 원 x 20% = 1만 4천 원, x 12 = 16만 8천 원 /
rates: 정률 환급률(일반 20, 청년·어르신 30, 3자녀 50, 저소득 53.3) + 정액형 기준금액 초과분 전액 / zero: 등록 안 하면 0원
사실(2026-11 기준): 월 15회 이상 이용 시 정률 환급(일반 20%·청년·2자녀·어르신 30%·3자녀 50%·저소득 53.3%), 정액형은 기준금액 초과분 전액,
매달 유리한 방식 자동 적용. 처음 이용자는 제휴 카드 발급 후 회원가입·카드 등록 필요. 기준금액 반값은 9월 이용분으로 종료(파이낸셜뉴스 10/18, 투데이신문).
usage: python3 bp48.py <scene> out.mp4 dur | out.jpg t1 t2 ..."""
import math, os, subprocess, sys
from PIL import Image
from bp30v2 import W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back, LINE, CYAN, YEL, HOT, COLD
from bp40 import lerp, mix, GREEN, DIM, BG_N

COIN = (236, 238, 244); COIN_D = (150, 156, 170); CARD = (246, 248, 252); MINT = (110, 230, 170)


def coin(c, x, y, r, a=1.0):
    c.circle(x, y + r * 0.12, r, fill=COIN_D, a=a)
    c.circle(x, y, r, fill=COIN, outline=(200, 205, 216), w=max(2, r * 0.08), a=a)
    c.circle(x, y, r * 0.72, outline=(210, 214, 224), w=max(2, r * 0.05), a=a)
    c.circle(x - r * 0.35, y - r * 0.35, r * 0.18, fill=(255, 255, 255), a=a * 0.8)


def tcard(c, x, y, s, a=1.0, tilt=0.0):
    w, h = 300 * s, 190 * s
    c.rrect((x - w / 2 + 8 * s, y - h / 2 + 12 * s, x + w / 2 + 8 * s, y + h / 2 + 12 * s), 22 * s, fill=(4, 14, 32), a=a * 0.6)
    c.rrect((x - w / 2, y - h / 2, x + w / 2, y + h / 2), 22 * s, fill=CARD, outline=(200, 210, 228), w=3, a=a)
    c.rrect((x - w / 2, y - h / 2 + 34 * s, x + w / 2, y - h / 2 + 66 * s), 0, fill=(70, 150, 255), a=a * 0.85)
    c.rrect((x - w / 2 + 28 * s, y - 6 * s, x - w / 2 + 84 * s, y + 36 * s), 8 * s, fill=(232, 196, 90), outline=(180, 140, 50), w=2, a=a)
    for i in range(3):
        c.line([(x - w / 2 + 28 * s, y + 4 * s + 10 * s * i), (x - w / 2 + 84 * s, y + 4 * s + 10 * s * i)], (180, 140, 50), 2, a)
    c.text(x + 40 * s, y + 52 * s, "모두의 카드", 30 * s, (30, 50, 90), a)


def tick(c, t):
    title(c, t, "")


# ---------------------------------------------------------------- 1. 가족 단톡방에 보내기
def send(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 48-A  |  가족에게 보내기")
    a0 = ease(t / 0.25)
    px0, py0, px1, py1 = 250, 320, 830, 1180
    c.rrect((px0 + 14, py0 + 18, px1 + 14, py1 + 18), 70, fill=(2, 10, 26), a=a0 * 0.6)
    c.rrect((px0, py0, px1, py1), 70, fill=(24, 30, 44), outline=(150, 165, 190), w=5, a=a0)
    c.rrect((px0 + 22, py0 + 24, px1 - 22, py1 - 24), 52, fill=(196, 214, 232), a=a0)
    c.rrect((px0 + 22, py0 + 24, px1 - 22, py0 + 130), 52, fill=(150, 176, 206), a=a0)
    c.rrect((px0 + 22, py0 + 90, px1 - 22, py0 + 130), 0, fill=(150, 176, 206), a=a0)
    c.text(540, py0 + 86, "우리 가족 (4)", 34, (20, 34, 60), a0)
    # 엄마 말풍선
    ka = back((t - 0.3) / 0.35)
    if t > 0.3:
        c.circle(px0 + 80, py0 + 210, 30, fill=(250, 200, 120), a=a0)
        c.rrect((px0 + 126, py0 + 170, px0 + 126 + 260 * max(ka, .05), py0 + 250), 24, fill=(255, 255, 255), a=a0)
        if ka > 0.7:
            c.text(px0 + 146, py0 + 210, "교통비 너무 많이 나와…", 26, (40, 40, 50), a0, anchor="lm")
    # 내가 보내는 영상 카드
    sk = back((t - 0.9) / 0.4)
    if t > 0.9:
        bx1 = px1 - 50; bx0 = bx1 - 330 * max(sk, .05); by0, by1 = py0 + 300, py0 + 620
        c.rrect((bx0, by0, bx1, by1), 26, fill=(255, 228, 92), a=a0)
        if sk > 0.6:
            c.rrect((bx0 + 18, by0 + 18, bx1 - 18, by1 - 80), 18, fill=(12, 30, 62), a=a0)
            c.circle((bx0 + bx1) / 2, (by0 + by1 - 62) / 2, 46, fill=(255, 255, 255), a=a0 * 0.9)
            c.poly([((bx0 + bx1) / 2 - 14, (by0 + by1 - 62) / 2 - 22), ((bx0 + bx1) / 2 - 14, (by0 + by1 - 62) / 2 + 22), ((bx0 + bx1) / 2 + 24, (by0 + by1 - 62) / 2)], (12, 30, 62), a0)
            c.text((bx0 + bx1) / 2, by1 - 42, "교통비 돌려받는 법", 28, (40, 30, 0), a0)
    # 보내기 버튼 + 날아가는 종이비행기
    c.rrect((px0 + 40, py1 - 130, px1 - 40, py1 - 60), 35, fill=(255, 255, 255), a=a0)
    pk = (t - 0.6) / 0.35
    c.circle(px1 - 90, py1 - 95, 30, fill=YEL if t > 0.6 else DIM, a=a0)
    if 0 < pk < 1:
        c.circle(px1 - 90, py1 - 95, 30 + 40 * eout(pk), outline=YEL, w=4, a=1 - pk)
    # 읽음 표시 + 하트
    if t > 1.7:
        ra = ease((t - 1.7) / 0.25)
        c.text(px1 - 400, py0 + 600, "읽음 3", 24, (90, 100, 120), ra, anchor="rm")
    if t > 2.0:
        hb = back((t - 2.0) / 0.4)
        c.circle(px0 + 80, py0 + 675, 30, fill=(250, 200, 120), a=a0)
        c.rrect((px0 + 126, py0 + 640, px0 + 126 + 250 * max(hb, .05), py0 + 710), 24, fill=(255, 255, 255), a=a0)
        if hb > 0.7:
            c.text(px0 + 146, py0 + 675, "고마워! 바로 할게 ♥", 26, (220, 60, 90), a0, anchor="lm")
    if t > 2.3:
        callout(c, W / 2, 1255, "가족에게 보내 주세요!", 60, YEL, ease((t - 2.3) / 0.12), 0.7 + 0.3 * back((t - 2.3) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


# ---------------------------------------------------------------- 2. 월 7만 원 → 1만 4천 원 → 1년 16만 8천 원
def calc(t0):
    base = BG.copy(); c = Canvas(); title(c, t0, "DWG. 48-B  |  얼마나 돌려받나 (수도권 일반, 월 7만 원)")
    t = t0 if t0 < 0.6 else (0.6 if t0 < 2.9 else 0.6 + (t0 - 2.9) * (4.2 / 4.9))
    a0 = ease(t0 / 0.25)
    cs = back((t - 0.1) / 0.45)
    bob = 8 * math.sin(t0 * 2.4)
    tcard(c, 300, 430 + bob, 1.05 * max(cs, 0.05), a0)
    if 0.7 < t0 < 2.9:
        sx = 300 - 170 + 340 * ((t0 - 0.7) / 1.0 % 1)
        c.line([(sx - 20, 340 + bob), (sx + 20, 520 + bob)], (255, 255, 255), 14, 0.35)
    c.text(300, 575, "예전 K-패스", 30, CYAN, a0 * ease((t - 0.5) / 0.3))
    # 15회 이상 탑승 눈금
    for i in range(15):
        on = t > 0.6 + i * 0.07
        x = 560 + (i % 5) * 84; y = 360 + (i // 5) * 70
        c.rrect((x - 32, y - 24, x + 32, y + 24), 12, fill=MINT if on else (14, 36, 70), outline=MINT if on else DIM, w=2, a=a0)
        if on:
            c.text(x, y, "✓", 28, (8, 40, 24), a0)
    c.text(770, 590, "한 달 15번 넘게", 34, MINT, a0 * ease((t - 1.6) / 0.3))
    # 큰 막대: 7만 원 중 20%
    bx0, bx1, by = 90, 990, 720
    k1 = ease((t - 1.9) / 0.6)
    if k1 > 0.03:
        c.rrect((bx0, by, bx0 + (bx1 - bx0) * k1, by + 90), 20, fill=(40, 80, 150), outline=LINE, w=3, a=a0)
    c.text(bx0 + 24, by + 45, "교통비 70,000원", 36, LINE, a0 * k1, anchor="lm")
    k2 = ease((t - 2.6) / 0.5)
    if k2 > 0:
        sx = bx1 - (bx1 - bx0) * 0.2
        c.rrect((sx, by, sx + (bx1 - sx) * k2, by + 90), 20, fill=MINT, a=1)
        c.text(sx + 10, by - 34, "20%", 36, MINT, k2, anchor="lm")
    # 동전 → 14,000원
    if t > 3.0:
        for i in range(5):
            kk = ease((t - 3.0 - 0.08 * i) / 0.4)
            coin(c, 900, lerp(by + 45, 940 - i * 20, kk), 46, kk)
        c.text(470, 905, "다음 달 14,000원 환급", 44, MINT, ease((t - 3.2) / 0.3), stroke=3)
    # x 12 → 168,000
    if t > 3.8:
        kc = ease((t - 3.8) / 1.0)
        v = int(14000 * (1 + 11 * kc))
        c.text(540, 1060, f"1년이면  {v:,}원", 66, YEL, 1, stroke=4)
        for m in range(12):
            on = kc * 12 >= m + 1
            c.circle(150 + m * 71, 1150, 20, fill=YEL if on else (14, 36, 70), outline=YEL if on else DIM, w=2, a=1)
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- 3. 환급률 + 기준 넘으면 전액
def rates(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 48-C  |  환급률 · 기준금액")
    a0 = ease(t / 0.25)
    rows = [("일반", 20, LINE), ("청년·어르신", 30, YEL), ("3자녀 이상", 50, MINT), ("저소득층", 53.3, MINT)]
    for i, (nm, pct, col) in enumerate(rows):
        y = 350 + i * 96
        k = eout((t - 0.2 - i * 0.15) / 0.6)
        c.text(250, y, nm, 34, col, a0, anchor="rm")
        c.rrect((280, y - 30, 980, y + 30), 16, fill=(14, 36, 70), outline=DIM, w=2, a=a0)
        w = 700 * pct / 60 * k
        if w > 4:
            c.rrect((280, y - 30, 280 + w, y + 30), 16, fill=mix(col, BG_N, 0.25), a=1)
        c.text(280 + w + 14 if w < 560 else 280 + w - 14, y, f"{pct:g}%", 34, col if w < 560 else (10, 30, 30), a0 * k, anchor="lm" if w < 560 else "rm")
    if t > 0.9:
        hl = 0.5 + 0.5 * math.sin(t * 8)
        c.rrect((40, 350 + 96 - 44, 1040, 350 + 96 + 44), 22, outline=YEL, w=4, a=0.5 + 0.5 * hl * ease((t - 0.9) / 0.3))
    # 정액형: 한 달 사용액 막대 + 기준선
    pa = ease((t - 2.4) / 0.3)
    c.text(540, 770, "많이 타면? 기준 넘는 돈은 전부!", 40, LINE, pa)
    cx0, cx1, cyb, cyt = 300, 780, 1170, 830
    kh = ease((t - 2.7) / 0.9)
    top = cyb - (cyb - cyt) * kh
    thr = cyb - (cyb - cyt) * 0.55
    if kh > 0:
        c.rrect((cx0, max(top, thr), cx1, cyb), 10, fill=(40, 80, 150), a=pa)
        if top < thr:
            c.rrect((cx0, top, cx1, thr), 10, fill=MINT, a=1)
            c.text(540, (top + thr) / 2, "전액 환급", 42, (8, 40, 24), ease((t - 3.4) / 0.2))
    if pa > 0:
        for xx in range(cx0 - 80, cx1 + 80, 34):
            c.line([(xx, thr), (xx + 18, thr)], YEL, 5, pa)
        c.text(cx1 + 90, thr - 30, "기준금액", 30, YEL, pa, anchor="lm")
        c.text(cx1 + 90, thr + 14, "(수도권 일반", 24, LINE, pa * 0.8, anchor="lm")
        c.text(cx1 + 90, thr + 46, " 6만 2천 원)", 24, LINE, pa * 0.8, anchor="lm")
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- 4. 등록 안 하면 0원
def zero(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 48-D  |  카드만 만들고 등록 안 하면")
    a0 = ease(t / 0.2)
    sh = 0.0
    if 0.9 < t < 1.25:
        sh = 14 * math.sin((t - 0.9) * 90) * (1 - (t - 0.9) / 0.35)
    # 영수증
    rx0, rx1, ry0, ry1 = 240 + sh, 840 + sh, 330, 1100
    c.rrect((rx0 + 12, ry0 + 16, rx1 + 12, ry1 + 16), 18, fill=(2, 10, 26), a=a0 * 0.6)
    c.rrect((rx0, ry0, rx1, ry1), 18, fill=(250, 250, 246), a=a0)
    for k in range(13):
        x = rx0 + k * (rx1 - rx0) / 12
        c.poly([(x - 23, ry1), (x, ry1 + 22), (x + 23, ry1)], (250, 250, 246), a0)
    c.text(540 + sh, ry0 + 70, "이번 달 교통비 환급", 40, (30, 40, 60), a0)
    c.line([(rx0 + 40, ry0 + 120), (rx1 - 40, ry0 + 120)], (190, 195, 205), 3, a0)
    for i, (k_, v) in enumerate([("이용 횟수", "46회"), ("쓴 돈", "70,000원"), ("카드 등록", "안 함")]):
        y = ry0 + 190 + i * 80
        c.text(rx0 + 50, y, k_, 34, (80, 90, 110), a0, anchor="lm")
        c.text(rx1 - 50, y, v, 34, HOT if v == "안 함" else (30, 40, 60), a0, anchor="rm")
    c.line([(rx0 + 40, ry0 + 430), (rx1 - 40, ry0 + 430)], (190, 195, 205), 3, a0)
    c.text(rx0 + 50, ry0 + 520, "환급", 44, (30, 40, 60), a0, anchor="lm")
    kz = ease((t - 0.6) / 0.3)
    c.text(rx1 - 50, ry0 + 520, "0원", 92, HOT, a0 * kz, anchor="rm", stroke=3)
    # 도장 쾅
    sk = (t - 0.9) / 0.25
    if sk > 0:
        s = 1.6 - 0.6 * eout(sk)
        cx, cy = 540 + sh, ry0 + 660
        c.rrect((cx - 200 * s, cy - 70 * s, cx + 200 * s, cy + 70 * s), 20 * s, outline=HOT, w=10 * s, a=min(1, sk * 2))
        c.text(cx, cy, "미등록", 84 * s, HOT, min(1, sk * 2), stroke=2)
        if sk < 1.6:
            c.circle(cx, cy, 120 + 260 * eout(min(sk, 1)), outline=(255, 255, 255), w=6, a=max(0, 1 - sk) * 0.8)
    if t > 1.6:
        callout(c, W / 2, 1255, "한 푼도 못 받아요!", 62, HOT, ease((t - 1.6) / 0.12), 0.7 + 0.3 * back((t - 1.6) / 0.3))
    return intro_fade(c.compose(base, glow=0.8), t).convert("RGB")


SCENES = {"send": send, "calc": calc, "rates": rates, "zero": zero}
if __name__ == "__main__":
    fn = SCENES[sys.argv[1]]; out = sys.argv[2]
    if out.endswith(".jpg"):
        ims = [fn(float(v)).resize((360, 640), Image.LANCZOS) for v in sys.argv[3:]]
        s = Image.new("RGB", (360 * len(ims), 640)); [s.paste(m, (i * 360, 0)) for i, m in enumerate(ims)]
        s.save(out, quality=86); raise SystemExit
    D = float(sys.argv[3]); tmp = out + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for n in range(int(round(D * FPS))):
        p.stdin.write(fn(n / FPS).tobytes())
    p.stdin.close(); assert p.wait() == 0
    os.replace(tmp, out); print("ok", out)
