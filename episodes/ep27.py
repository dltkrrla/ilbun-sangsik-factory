"""27편 - 줄자 끝 쇠고리가 헐렁한 이유 (전부 2D, 사람 없음 — 매일 쓰는 물건의 숨은 이유)
사실: 줄자 끝 고리는 리벳 구멍이 길쭉해서 '고리 두께만큼' 앞뒤로 움직인다. 물건 끝에 걸면 고리가 빠져나와 안쪽 면이 0,
벽에 대고 밀면 고리가 들어가 바깥 면이 0 → 걸어도 밀어도 고리 두께가 치수에 끼어들지 않는다 (This Old House "What makes it wiggle",
Mental Floss "Why are the ends of measuring tapes so loose" — 미국식 줄자 고리 1/16인치 ≈ 1.6mm, Pro Tool Reviews).
고리를 고정하거나 리벳을 두드려 조이면 이 보정이 사라져 치수가 틀어진다.
가설(플레이북 H14): 첫 문장을 질문 대신 '숫자가 든 단정형'으로, 같은 숫자(1mm)를 0초 화면에 큰 글자로."""
import math
from kit import *
from vtl import build, main

BG1 = (34, 44, 78)
BG2 = (40, 56, 96)
BLADE = (252, 204, 48)
BLADE_D = (214, 160, 20)
STEEL = (168, 174, 186)
STEEL_D = (104, 110, 124)
CASE = (232, 84, 52)
CASE_D = (150, 44, 30)
GRIP = (44, 46, 54)
WOOD = (196, 140, 86)
WOOD_D = (150, 100, 58)
WALL = (214, 218, 228)


def cam(z=1.0, fx=540, fy=760):
    return (C0[0] * z, fx, fy)


def tape(d, cm, Z, y, h, s, th, x_left=-400, ticks=True, num_scale=1.0):
    """Horizontal blade whose scale zero sits at x=Z. Hook plate thickness th.
    s=1: hook pulled out (plate spans Z..Z+th) · s=0: pushed in (plate spans Z-th..Z)."""
    bend = Z - th  # blade metal ends here so the hook can slide back
    rr(d, cm, x_left, y, bend + 2, y + h, 6, fill=BLADE + (255,))
    rr(d, cm, x_left, y + h - 8, bend + 2, y + h, 3, fill=BLADE_D + (255,))
    if ticks:
        step = h * 0.42
        i = 0
        x = Z
        while x > x_left:
            if x < bend - 4:
                L = h * (0.55 if i % 10 == 0 else 0.34 if i % 5 == 0 else 0.2)
                d.line([cxy(cm, x, y + 2), cxy(cm, x, y + L)], fill=INK + (255,), width=max(1, int(3 * cm[0] * SC * num_scale)))
                if i % 10 == 0 and i > 0:
                    txt(d, cm, x, y + h * 0.75, str(i // 10), h * 0.32, RED if i == 10 else INK)
            i += 1
            x -= step
    off = (s - 1.0) * th  # 0 when pulled out, -th when pushed in
    px0 = Z + off
    # tab riveted on top of blade (slides with the plate)
    rr(d, cm, px0 - h * 1.25, y - 4, px0 + 2, y + h * 0.55, 6, fill=STEEL + (255,), outline=STEEL_D + (255,), width=2)
    for k in (0.45, 0.9):
        cx = px0 - h * k * 1.1
        # elongated slot in the blade (fixed) + rivet (moves with hook)
        rr(d, cm, Z - h * k * 1.1 - th - 6, y + h * 0.12, Z - h * k * 1.1 + 6, y + h * 0.42, 8, fill=(60, 60, 70, 255))
        circ(d, cm, cx, y + h * 0.27, h * 0.11, fill=(230, 232, 238, 255), outline=STEEL_D + (255,), width=2)
    # bent-down plate
    rr(d, cm, px0, y - 4, px0 + th, y + h + h * 0.9, 4, fill=STEEL + (255,), outline=STEEL_D + (255,), width=2)
    return px0


def case(d, cm, x, y, w, hgt):
    rr(d, cm, x - w / 2, y - hgt / 2, x + w / 2, y + hgt / 2, hgt * 0.32, fill=CASE + (255,), outline=CASE_D + (255,), width=4)
    rr(d, cm, x - w / 2 + 18, y + hgt * 0.12, x + w / 2 - 18, y + hgt / 2 - 14, 20, fill=GRIP + (255,))
    circ(d, cm, x - w * 0.1, y - hgt * 0.12, hgt * 0.16, fill=(255, 255, 255, 230))
    rr(d, cm, x - w * 0.15, y - hgt * 0.42, x + w * 0.2, y - hgt * 0.3, 6, fill=GRIP + (255,))


def arrows(d, cm, x, y, span, t, col=YEL, a=255):
    for sgn in (-1, 1):
        tip = x + sgn * (span + 8 * math.sin(t * 9))
        d.line([cxy(cm, x + sgn * 14, y), cxy(cm, tip, y)], fill=col + (a,), width=int(8 * cm[0] * SC))
        d.polygon([cxy(cm, tip + sgn * 22, y), cxy(cm, tip, y - 16), cxy(cm, tip, y + 16)], fill=col + (a,))


def dim(d, cm, x0, x1, y, col=YEL, label=None, size=46):
    for x in (x0, x1):
        d.line([cxy(cm, x, y - 40), cxy(cm, x, y + 40)], fill=col + (255,), width=int(5 * cm[0] * SC))
    d.line([cxy(cm, x0, y), cxy(cm, x1, y)], fill=col + (255,), width=int(5 * cm[0] * SC))
    if label:
        txt(d, cm, (x0 + x1) / 2, y + 62, label, size, col)


# ---------------- scenes (r = seconds since the scene started) ----------------
def sHook(r, im, d):
    """H3: 0초부터 고리가 앞뒤로 덜컥덜컥 + 카메라 밀어 들어감. 답(걸기/밀기)은 아직 숨김."""
    panel(d, BG1)
    z = 1.0 + 0.35 * ease(r / 2.2)
    cm = cam(z, 600, 700)
    s = 0.5 + 0.5 * math.copysign(min(1, abs(math.sin(r * 6.0)) * 1.6), math.sin(r * 6.0))
    case(d, cm, 250, 700, 300, 260)
    tape(d, cm, 780, 610, 110, s, 56, x_left=320)
    arrows(d, cm, 808, 500, 80, r)
    if r > 1.3:
        pill(d, C0, 300, 420, "고장?", 60, RED, WHITE, sc=kpop(r, 1.3))
    if r > 2.8:
        rings(d, cm, 808, 690, 120, r - 2.8, col=YEL)
        badge(d, C0, 560, 420, 50, YEL, "!", kpop(r, 2.8, .25))


def sThick(r, im, d):
    panel(d, BG2)
    cm = cam(1.25, 640, 740)
    s = 1.0 if r < 0.7 else max(0.0, 1 - ease((r - 0.7) / 0.5))
    tape(d, cm, 720, 640, 100, s, 60, x_left=120)
    # dimension: travel (Z-60..Z) vs plate thickness
    if r > 1.2:
        dim(d, cm, 660, 720, 585, YEL, None)
        dim(d, cm, 660, 720, 870, YEL, None)
        txt(d, cm, 560, 585, "움직인 거리", 32, WHITE, a=255 * ease((r - 1.2) / .3))
        txt(d, cm, 560, 870, "고리 두께", 32, YEL, a=255 * ease((r - 1.4) / .3))
        pill(d, C0, 540, 1150, "=  딱 1mm 남짓", 50, YEL, INK, sc=kpop(r, 1.6))


def sWrong(r, im, d):
    """H12 리훅(6초쯤): 화면 반전 — 빨간 경고."""
    panel(d, (96, 36, 44) if r < 0.25 else (60, 34, 52))
    cm = cam(1.0)
    rr(d, cm, 150, 520, 930, 640, 12, fill=WOOD + (255,), outline=WOOD_D + (255,), width=4)
    rr(d, cm, 150, 700, 930, 790, 6, fill=BLADE + (255,))
    for i in range(0, 39):
        x = 170 + i * 20
        d.line([cxy(cm, x, 700), cxy(cm, x, 700 + (40 if i % 10 == 0 else 24 if i % 5 == 0 else 14))], fill=INK + (255,), width=int(3 * SC))
    shake = 10 * math.sin(r * 50) * max(0, 1 - r / 0.6)
    pill(d, C0, 540 + shake, 900, "치수 틀림", 64, RED, WHITE, sc=kpop(r, 0.15))
    if r > 0.8:
        txt(d, C0, 540, 420, "±1mm", 110 * kpop(r, 0.8, .25) + 1, YEL)
    if r > 1.6:
        badge(d, C0, 870, 470, 56, RED, "x", kpop(r, 1.6, .25))


def _board_scene(r, im, d, mode):
    panel(d, BG2)
    cm = cam(1.15, 600, 760)
    Z = 700
    if mode == "hook":
        # board's right edge at Z; hook plate grabs it from outside and slides OUT
        rr(d, cm, 380, 760, Z, 1000, 10, fill=WOOD + (255,), outline=WOOD_D + (255,), width=4)
        for k in range(4):
            d.line([cxy(cm, 400, 800 + k * 50), cxy(cm, Z - 20, 790 + k * 52)], fill=WOOD_D + (180,), width=int(3 * SC))
        s = 0.0 + ease((r - 0.3) / 0.6)
        pull = -30 * ease((r - 0.3) / 0.6)
        tape(d, cm, Z, 664, 90, s, 46, x_left=Z - 900 + pull)
        d.line([cxy(cm, 420, 600), cxy(cm, 330, 600)], fill=WHITE + (220,), width=int(8 * SC))
        d.polygon([cxy(cm, 305, 600), cxy(cm, 335, 580), cxy(cm, 335, 620)], fill=WHITE + (220,))
        txt(d, cm, 375, 555, "당겨요", 34, WHITE)
    else:
        # wall at Z..; tape pushed right, hook slides IN until its outer face touches the wall
        rr(d, cm, Z, 380, Z + 300, 1140, 0, fill=WALL + (255,))
        for k in range(8):
            d.line([cxy(cm, Z + 10, 420 + k * 95), cxy(cm, Z + 290, 420 + k * 95)], fill=(186, 190, 202, 255), width=int(3 * SC))
        s = 1.0 - ease((r - 0.3) / 0.6)
        tape(d, cm, Z, 664, 90, s, 46, x_left=-300)
        d.line([cxy(cm, 330, 600), cxy(cm, 420, 600)], fill=WHITE + (220,), width=int(8 * SC))
        d.polygon([cxy(cm, 445, 600), cxy(cm, 415, 580), cxy(cm, 415, 620)], fill=WHITE + (220,))
        txt(d, cm, 375, 555, "밀어요", 34, WHITE)
    if r > 1.0:
        dashed(d, cm, (Z, 520), (Z, 1040), YEL + (255,), wd=6)
        circ(d, cm, Z, 1060, 40 * kpop(r, 1.0, .25), fill=YEL + (255,))
        txt(d, cm, Z, 1060, "0", 50 * kpop(r, 1.0, .25) + 1, INK)
    if r > 1.6:
        badge(d, cm, Z + (-120 if mode == "push" else 120), 1060, 42, GREEN, "check", kpop(r, 1.6, .25))


def sOut(r, im, d):
    _board_scene(r, im, d, "hook")
    pill(d, C0, 540, 360, "걸면 → 쭉 빠짐", 48, YEL, INK, sc=kpop(r, 0.1))


def sIn(r, im, d):
    _board_scene(r, im, d, "push")
    pill(d, C0, 540, 360, "밀면 → 쏙 들어감", 48, YEL, INK, sc=kpop(r, 0.1))


def sBoth(r, im, d):
    panel(d, BG1)
    for row, (mode, y0) in enumerate((("hook", 520), ("push", 900))):
        cm = (C0[0] * 0.62, 540, 760 + (row - 0.5) * 0 )
        Z = 640
        yb = y0 - 60
        if mode == "hook":
            rr(d, C0, 330, y0 - 30, 640, y0 + 70, 8, fill=WOOD + (255,))
            tape(d, C0, Z, yb - 40, 56, 1.0, 26, x_left=150)
        else:
            rr(d, C0, Z, y0 - 140, Z + 220, y0 + 90, 0, fill=WALL + (255,))
            tape(d, C0, Z, yb - 40, 56, 0.0, 26, x_left=150)
        dashed(d, C0, (Z, y0 - 150), (Z, y0 + 100), YEL + (255,), wd=5)
        badge(d, C0, 900, y0 - 40, 50, GREEN, "check", kpop(r, 0.3 + row * 0.5, .25))
    pill(d, C0, 540, 1140, "0이 딱 물건 끝", 56, YEL, INK, sc=kpop(r, 1.2))


def sTighten(r, im, d):
    panel(d, (60, 34, 52))
    cm = cam(1.2, 620, 760)
    tape(d, cm, 760, 700, 90, 0.5, 46, x_left=200)
    hit = (r * 2.2) % 1
    emo(im, 830, 500 - 60 * (1 - hit), 190, "🔨", cam=cm, rot=30 - 50 * hit)
    if r > 0.5:
        circ(d, cm, 800, 680, 30 + 50 * hit, outline=(255, 255, 255, int(200 * (1 - hit))), width=6)
    if r > 1.0:
        badge(d, C0, 300, 480, 66, RED, "x", kpop(r, 1.0, .25))
        pill(d, C0, 540, 1120, "오히려 틀려요", 58, RED, WHITE, sc=kpop(r, 1.2))


def sTry(r, im, d):
    panel(d, BG2)
    cm = cam(1.0)
    wob = math.sin(r * 14) * 6
    case(d, cm, 330, 800 + wob, 300, 260)
    s = 0.5 + 0.5 * math.sin(r * 12)
    tape(d, cm, 860, 720 + wob, 80, s, 40, x_left=400)
    emo(im, 900, 960, 180, "👆", rot=-20 + 10 * math.sin(r * 12))
    arrows(d, cm, 880, 600, 60, r)
    pill(d, C0, 540, 420, "덜컥덜컥 = 정상", 54, GREEN, WHITE, sc=kpop(r, 0.5))


def sEnd(r, im, d):
    """H13 루프: 첫 장면과 같은 구도(케이스 + 덜컥이는 고리)."""
    panel(d, BG1)
    cm = cam(1.2, 600, 700)
    s = 0.5 + 0.5 * math.copysign(min(1, abs(math.sin(r * 6.0)) * 1.6), math.sin(r * 6.0))
    case(d, cm, 250, 700, 300, 260)
    tape(d, cm, 780, 610, 110, s, 56, x_left=320)
    arrows(d, cm, 808, 500, 80, r)
    emo(im, 300, 420, 120 * kpop(r, 0.3, .25), "📲")


SPOKEN = [
    "줄자 끝 쇠고리, 고장 아니에요. 딱 일 밀리 남짓, 일부러 흔들려요.",
    "흔들리는 거리는, 딱 고리 두께만큼이에요.",
    "왜냐고요? 이게 없으면, 치수가 틀려요.",
    "물건 끝에 걸면, 고리가 두께만큼 쭉 빠져나오고,",
    "벽에 대고 밀면, 두께만큼 쏙 들어가요.",
    "그래서 걸어도 밀어도, 영 눈금이 딱 물건 끝에 맞죠.",
    "헐렁하다고 꽉 조이면, 오히려 치수가 틀려져요.",
    "집에 줄자 있으면, 지금 끝을 한번 흔들어 보세요!",
    "이사 준비하는 친구에게 보내 주세요! 팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (2, 5)
LINES = [
    ("", None, None, sHook),
    ("", [("흔들리는 거리 =", W_)], [("딱 ", W_), ("고리 두께", Y_)], sThick),
    ("", [("이게 없으면", W_)], [("치수가 틀려요", Y_)], sWrong),
    ("", [("물건 끝에 ", W_), ("걸면", Y_)], [("고리가 쭉 빠져나오고", W_)], sOut),
    ("", [("벽에 대고 ", W_), ("밀면", Y_)], [("쏙 들어가요", W_)], sIn),
    ("", [("걸어도 밀어도", W_)], [("0", Y_), ("이 딱 물건 끝에", W_)], sBoth),
    ("", [("헐렁하다고 ", W_), ("꽉 조이면", Y_)], [("오히려 치수가 틀려요", W_)], sTighten),
    ("", [("지금 줄자 끝을", W_)], [("흔들어 보세요!", Y_)], sTry),
    ("", [("이사하는 친구에게 보내요", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)], sEnd),
]
T = (("줄자 끝 고리", Y_), ("가 헐렁한 이유", W_))
Q = [[[("줄자 끝 고리", W_)]], [[("딱 ", W_), ("1mm", Y_), (" 헐렁", W_)]]]
EV = lambda s: [("click", 0.1), ("click", 0.6), ("click", 1.1), ("pop", s[1] + 0.7, 700), ("ding", s[1] + 1.6, 1320),
                ("buzz", s[2] + 0.05), ("thud", s[2] + 0.8, .4), ("whoosh", s[3] + 0.3), ("click", s[3] + 0.9),
                ("whoosh", s[4] + 0.3), ("click", s[4] + 0.9), ("yes", s[5] + 0.3), ("yes", s[5] + 0.8), ("ding", s[5] + 1.2, 1568),
                ("thud", s[6] + 0.3, .4), ("no", s[6] + 1.0), ("pop", s[7] + 0.5, 800), ("pop", s[8] + 0.3, 1000)]
EP = build(27, "ep27", LINES, T, Q, EV, qsize=110, qys=(1080, 1200), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e27")
