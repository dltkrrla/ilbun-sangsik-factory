"""49편 "엄마 나 폰 깨졌어" 자녀 사칭 메신저피싱 설계도 4장면.
chat: 수상한 대화창 + 빨간 경고 / remote: 원격 조종 앱이 통장 돈을 빼감 / loan: 신분증·카드 사진 → 대출 / check: 막는 법 체크리스트
사실: 경기남부경찰청 2026-07 검거(538명·44억 5천만 원, "엄마 나 폰 깨져서… 링크 설치해줘" → 원격제어 앱 → 예금 인출·신분증으로 대출 — 인사이트) ·
신분증·카드 사진 요구(위키트리) · 본인 번호로 확인(보안뉴스) · 신분증·카드 사진 보내지 말고 모르는 링크 누르지 말기(전남경찰청).
usage: python3 bp49.py <scene> out.mp4 dur | out.jpg t1 t2 ..."""
import math, os, subprocess, sys
from PIL import Image
from bp30v2 import W, H, FPS, BG, Canvas, F, callout, title, intro_fade, ease, eout, back, LINE, CYAN, YEL, HOT, COLD
from bp40 import lerp, mix, GREEN, DIM, BG_N

MINT = (110, 230, 170); RED = (255, 90, 80)


def phone(c, a, x0=250, y0=320, x1=830, y1=1180, head="모르는 번호", hcol=(150, 176, 206)):
    c.rrect((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 70, fill=(2, 10, 26), a=a * 0.6)
    c.rrect((x0, y0, x1, y1), 70, fill=(24, 30, 44), outline=(150, 165, 190), w=5, a=a)
    c.rrect((x0 + 22, y0 + 24, x1 - 22, y1 - 24), 52, fill=(196, 214, 232), a=a)
    c.rrect((x0 + 22, y0 + 24, x1 - 22, y0 + 130), 52, fill=hcol, a=a)
    c.rrect((x0 + 22, y0 + 90, x1 - 22, y0 + 130), 0, fill=hcol, a=a)
    c.text((x0 + x1) / 2, y0 + 86, head, 34, (20, 34, 60), a)


def bubble(c, x, y, s, k, a, fill=(255, 255, 255), col=(40, 40, 50), size=28):
    if k <= 0: return 0
    w = F(size).getlength(s) + 40
    kk = max(0.05, min(1.0, k))
    c.rrect((x, y - 34, x + w * kk, y + 34), 26, fill=fill, a=a)
    if k > 0.7:
        c.text(x + 20, y, s, size, col, a, anchor="lm")
    return w


def flag(c, x, y, s, k):
    if k <= 0: return
    sc = 0.6 + 0.4 * back(k)
    w = F(26 * sc).getlength(s) + 60 * sc
    c.rrect((x, y - 24 * sc, x + w, y + 24 * sc), 24 * sc, fill=(70, 14, 14), outline=RED, w=3, a=min(1, k * 2))
    c.text(x + 14 * sc, y, "⚠", 26 * sc, RED, min(1, k * 2), anchor="lm")
    c.text(x + 44 * sc, y, s, 26 * sc, (255, 200, 195), min(1, k * 2), anchor="lm")


# ---------------------------------------------------------------- 1. 수상한 대화창
def chat(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 49-A  |  자녀 사칭 문자")
    a0 = ease(t / 0.25)
    phone(c, a0, 170, 320, 750, 1180)
    msgs = [(0.3, "엄마 나야 폰 깨졌어 ㅠ", 520), (1.0, "수리 맡겨서 이 번호로 연락해", 620),
            (6.0, "보험 신청해야 돼", 720), (6.6, "이 링크 눌러서 앱 깔아 줘", 820)]
    for th, s, y in msgs:
        bubble(c, 210, y, s, back((t - th) / 0.35), a0)
    lk = back((t - 7.2) / 0.35)
    if lk > 0:
        c.rrect((210, 880, 210 + 380 * max(lk, .05), 960), 22, fill=(255, 255, 255), a=a0)
        if lk > 0.7:
            c.text(230, 920, "http://●●●●●.●●/repair", 26, (40, 90, 200), a0, anchor="lm")
    # 빨간 경고 꼬리표 (오른쪽)
    flag(c, 640, 520, "고장 핑계", (t - 1.6) / 0.3)
    flag(c, 640, 620, "새 번호", (t - 2.0) / 0.3)
    flag(c, 640, 920, "앱 설치 링크", (t - 7.7) / 0.3)
    if t > 7.7:
        pul = 0.5 + 0.5 * math.sin(t * 9)
        c.rrect((196, 872, 604, 968), 26, outline=RED, w=5, a=0.4 + 0.6 * pul)
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- 2. 원격 조종
def remote(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 49-B  |  원격 조종 앱")
    a0 = ease(t / 0.25)
    phone(c, a0, 250, 380, 830, 1180, head="내 통장", hcol=(170, 200, 230))
    bal = 3450000
    kd = ease((t - 0.9) / 0.8)
    v = int(bal * (1 - kd))
    c.text(540, 600, "잔액", 32, (60, 70, 90), a0)
    c.text(540, 680, f"{v:,}원", 70, RED if kd > 0 else (20, 34, 60), a0, stroke=0)
    bx0, by0, bx1, by1 = 340, 880, 740, 980
    press = 0.7 < t < 0.95
    c.rrect((bx0, by0, bx1, by1), 40, fill=(60, 110, 230) if not press else (30, 70, 180), a=a0)
    c.text(540, 930, "이체", 40, (255, 255, 255), a0)
    # 혼자 움직이는 커서
    if t > 0.15:
        k = eout((t - 0.15) / 0.55)
        cx = lerp(800, 560, k) + 6 * math.sin(t * 13); cy = lerp(520, 935, k)
        c.poly([(cx, cy), (cx, cy + 56), (cx + 15, cy + 42), (cx + 28, cy + 66), (cx + 38, cy + 61), (cx + 25, cy + 37), (cx + 44, cy + 36)], (255, 255, 255), 1)
        if press:
            c.circle(560, 935, 30 + 120 * (t - 0.7) / 0.25, outline=RED, w=5, a=1 - (t - 0.7) / 0.25)
    # 원격 신호 (오른쪽 위)
    sx, sy = 920, 330
    for i in range(3):
        k = ((t * 1.4 + i / 3) % 1)
        r = 30 + 90 * k
        c.line([(sx + r * math.cos(a_), sy + r * math.sin(a_)) for a_ in [math.pi * (0.6 + 0.8 * q / 12) for q in range(13)]], RED, 6, a0 * (1 - k))
    c.circle(sx, sy, 16, fill=RED, a=a0)
    c.text(sx - 40, sy - 70, "누군가 조종 중", 28, RED, a0 * ease((t - 0.2) / 0.3), anchor="rm")
    # 빠져나가는 돈
    if kd > 0:
        for i in range(8):
            k = ((t * 1.6 + i / 8) % 1)
            al = (1 - k) * min(1, kd * 3)
            x_, y_ = lerp(790, 910, k), lerp(600, 330, k)
            c.circle(x_, y_ + 3, 22, fill=(170, 130, 30), a=al); c.circle(x_, y_, 22, fill=YEL, a=al); c.text(x_, y_, "원", 20, (90, 60, 0), al)
    if t > 1.6:
        callout(c, W / 2, 1265, "휴대폰이 남의 손에!", 60, RED, ease((t - 1.6) / 0.12), 0.7 + 0.3 * back((t - 1.6) / 0.3))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- 3. 신분증·카드 사진 → 대출
def idcard(c, x, y, s, a):
    c.rrect((x - 150 * s, y - 95 * s, x + 150 * s, y + 95 * s), 16 * s, fill=(236, 244, 250), outline=(180, 196, 214), w=3, a=a)
    c.rrect((x - 130 * s, y - 70 * s, x - 40 * s, y + 50 * s), 10 * s, fill=(196, 208, 224), a=a)
    c.circle(x - 85 * s, y - 25 * s, 24 * s, fill=(150, 164, 186), a=a)
    c.rrect((x - 120 * s, y + 10 * s, x - 50 * s, y + 50 * s), 14 * s, fill=(150, 164, 186), a=a)
    for i in range(3):
        c.rrect((x - 20 * s, y - 55 * s + i * 36 * s, x + (120 - 30 * i) * s, y - 39 * s + i * 36 * s), 6 * s, fill=(196, 208, 224), a=a)
    c.text(x + 40 * s, y + 70 * s, "신분증", 24 * s, (60, 80, 110), a)


def ccard(c, x, y, s, a):
    c.rrect((x - 150 * s, y - 95 * s, x + 150 * s, y + 95 * s), 18 * s, fill=(46, 70, 120), outline=(120, 150, 210), w=3, a=a)
    c.rrect((x - 120 * s, y - 30 * s, x - 66 * s, y + 10 * s), 8 * s, fill=(232, 196, 90), a=a)
    c.text(x - 110 * s, y + 52 * s, "●●●●  ●●●●  ●●●●", 20 * s, (220, 230, 250), a, anchor="lm")


def loan(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 49-C  |  사진 두 장이면")
    a0 = ease(t / 0.25)
    k1 = back((t - 0.2) / 0.4); k2 = back((t - 0.6) / 0.4)
    idcard(c, 300, 440, max(k1, .05) * 1.0, a0)
    ccard(c, 780, 440, max(k2, .05) * 1.0, a0)
    # 찰칵 (사진)
    for th, x in ((0.5, 300), (0.9, 780)):
        if 0 < t - th < 0.25:
            c.rrect((x - 170, 330, x + 170, 550), 20, fill=(255, 255, 255), a=1 - (t - th) / 0.25)
    # 두 갈래 화살표 → 통장 / 대출
    ka = ease((t - 1.3) / 0.5)
    if ka > 0:
        c.arrow(300, 560, 300, 560 + 200 * ka, RED, 8, 26, 1)
        c.arrow(780, 560, 780, 560 + 200 * ka, RED, 8, 26, 1)
    kb = back((t - 1.8) / 0.4)
    if kb > 0:
        for x, s1, s2 in ((300, "통장 잔액", "전부 이체"), (780, "내 이름으로", "대출 실행")):
            c.rrect((x - 200, 800, x + 200, 1000), 26, fill=(60, 16, 18), outline=RED, w=4, a=min(1, kb))
            c.text(x, 860, s1, 36 * max(kb, .3), (255, 200, 195), min(1, kb))
            c.text(x, 935, s2, 46 * max(kb, .3), RED, min(1, kb), stroke=2)
    if t > 2.6:
        sk = (t - 2.6) / 0.25
        s = 1.5 - 0.5 * eout(min(sk, 1))
        c.rrect((780 - 150 * s, 1050 - 46 * s, 780 + 150 * s, 1050 + 46 * s), 14 * s, outline=RED, w=8 * s, a=min(1, sk * 2))
        c.text(780, 1050, "대출까지!", 50 * s, RED, min(1, sk * 2), stroke=2)
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


# ---------------------------------------------------------------- 4. 막는 법
def check(t):
    base = BG.copy(); c = Canvas(); title(c, t, "DWG. 49-D  |  막는 법")
    a0 = ease(t / 0.25)
    items = [(0.2, "원래 번호로 직접 전화", MINT), (1.0, "링크 누르지 않기", MINT),
             (1.8, "신분증·카드 사진 보내지 않기", MINT), (3.4, "보냈다면 바로 112 신고", YEL)]
    for i, (th, s, col) in enumerate(items):
        y = 400 + i * 170
        k = back((t - th) / 0.4)
        if k <= 0:
            c.rrect((90, y - 62, 990, y + 62), 30, outline=DIM, w=2, a=a0 * 0.4)
            continue
        kk = min(1, k)
        c.rrect((90 - 20 * (1 - kk), y - 62, 990, y + 62), 30, fill=(10, 34, 66), outline=col, w=4, a=kk)
        c.circle(170, y, 40, fill=col, a=kk)
        c.text(170, y + 2, "✓", 48 * max(k, .3), (8, 30, 30), kk)
        c.text(240, y, s, 44, LINE, kk, anchor="lm")
    if t > 3.6:
        pk = back((t - 3.6) / 0.35)
        c.circle(540, 1160, 80 * max(pk, .05), fill=YEL, a=1)
        c.text(540, 1160, "112", 60 * max(pk, .3), (40, 30, 0), 1, stroke=0)
        for i in range(3):
            r = 96 + 22 * i + 10 * math.sin(t * 6 + i)
            c.circle(540, 1160, r, outline=YEL, w=4, a=0.5 / (i + 1))
    return intro_fade(c.compose(base, glow=0.85), t).convert("RGB")


SCENES = {"chat": chat, "remote": remote, "loan": loan, "check": check}
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
