"""20편 - 엘리베이터 거울은 왜 있을까 (첫 문장: 행동 공감 + "99%가 모르는" 도전형. 벤치마크: 오늘의집 쇼츠 \"99%는 틀리는\", 셀카 질문형)
사실: 장애인·노인·임산부 등의 편의증진 보장에 관한 법률 시행규칙 [별표 1] 9. 장애인용 승강기 라.(2)
"승강기 내부에서 휠체어가 180도 회전이 불가능할 경우, 휠체어가 후진하여 문의 개폐여부를 확인하거나 내릴 수 있도록
승강기 후면의 0.6미터 이상의 높이에 견고한 재질의 거울을 설치" (law.go.kr). 교통약자법 시행규칙도 후면 거울 규정
(바닥 1.4m×1.4m 이상이면 예외). → '모든 엘리베이터'가 아니라 '법이 정한 이유'로 말한다."""
import math, os
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

WALL = (206, 212, 224)
WALL2 = (176, 184, 200)
GLASS = (186, 224, 246)
DOOR = (150, 158, 172)
BG = (52, 62, 98)


def car(d, door=0.0, mirror_glow=0.0):
    """Side cut of an elevator: back wall (mirror) on the left, sliding door on the right."""
    rr(d, C0, 170, 500, 910, 1120, 16, fill=WALL + (255,))
    rr(d, C0, 170, 1090, 910, 1120, 6, fill=WALL2 + (255,))          # floor
    rr(d, C0, 150, 480, 930, 510, 8, fill=(120, 128, 146, 255))       # ceiling
    rr(d, C0, 150, 1110, 930, 1140, 8, fill=(120, 128, 146, 255))
    # mirror on the back wall, 0.6 m up
    g = mix(GLASS, (255, 255, 210), mirror_glow)
    rr(d, C0, 186, 600, 222, 1010, 6, fill=g + (255,), outline=WHITE + (255,), width=4)
    # door (slides up = open, in this side cut)
    h = 560 * (1 - door)
    if h > 4:
        rr(d, C0, 888, 520, 918, 520 + h, 4, fill=DOOR + (255,))


def chair(im, x, y, size=270, a=1.0):
    """🧑‍🦽 faces left = toward the back wall (the mirror)."""
    emo(im, x, y, size, "🧑‍🦽", a=a)


def arrow(d, x0, y0, x1, y1, col=YEL, w=10, a=255):
    d.line([cxy(C0, x0, y0), cxy(C0, x1, y1)], fill=col + (a,), width=w)
    ang = math.atan2(y1 - y0, x1 - x0)
    for s in (-1, 1):
        hx = x1 - 34 * math.cos(ang + s * .5); hy = y1 - 34 * math.sin(ang + s * .5)
        d.line([cxy(C0, x1, y1), cxy(C0, hx, hy)], fill=col + (a,), width=w)


def dashed(d, x0, y0, x1, y1, k=1.0, col=(240, 170, 0), w=11):
    n = 14
    for i in range(int(n * k)):
        a0, a1 = i / n, (i + .55) / n
        d.line([cxy(C0, lerp(x0, x1, a0), lerp(y0, y1, a0)), cxy(C0, lerp(x0, x1, a1), lerp(y0, y1, a1))], fill=col + (255,), width=w)


# ---------------- 3D photo layer (Blender renders, ../work/blender/r20) ----------------
R3D = os.environ.get("EP20_3D", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "blender", "r20"))
_pc, FPS3D = {}, 12
PX0, PY0, PX1, PY1 = 70, 280, 1010, 1240          # panel in world coords


def _img(name):
    if name not in _pc:
        _pc[name] = Image.open(os.path.join(R3D, name + ".png")).convert("RGBA")
    return _pc[name]


def photo(im, name, z=1.0, a=1.0, fx=0.5, fy=0.5):
    """Paste a render into the panel (cover fit, zoom z around (fx, fy)), rounded corners."""
    X0, Y0 = cxy(C0, PX0, PY0); X1, Y1 = cxy(C0, PX1, PY1)
    w, h = int(X1 - X0), int(Y1 - Y0)
    src = _img(name); sw, sh = src.size
    sc_ = max(w / sw, h / sh) * z
    cw, ch = w / sc_, h / sc_
    cx, cy = fx * sw, fy * sh
    l = min(max(cx - cw / 2, 0), sw - cw); t = min(max(cy - ch / 2, 0), sh - ch)
    crop = src.crop((int(l), int(t), int(l + cw), int(t + ch))).resize((w, h), Image.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], int(70 * C0[0] * SC), fill=int(255 * a))
    im.paste(crop, (int(X0), int(Y0)), mask)
    return (l, t, cw, ch, sw, sh)


def at(view, u, v):
    """Image-normalized (u, v) of the render -> world coords on screen, given photo()'s returned view."""
    l, t, cw, ch, sw, sh = view
    return PX0 + (u * sw - l) / cw * (PX1 - PX0), PY0 + (v * sh - t) / ch * (PY1 - PY0)


def seq(prefix, n, r):
    return f"{prefix}_{min(n - 1, max(0, int(r * FPS3D))):03d}"


def flash(im, x, y, k):
    if k > 0:
        L = Image.new("RGBA", im.size, (0, 0, 0, 0))
        circ(ImageDraw.Draw(L), C0, x, y, 30 + 120 * (1 - k), fill=(255, 255, 255, int(235 * k)))
        im.alpha_composite(L)


# ---------------- scenes (r = seconds since the scene started) ----------------
def sHook(r, im, d):
    """Real person (Google Flow / Veo clip, jump cut 0-1.9s + 4.4-7.8s) checks his hair in the lift mirror.
    No wheelchair here: the answer is revealed only on the next line ("진짜 이유는 휠체어")."""
    panel(d, BG)
    photo(im, f"flow_{min(160, int(r * 30) + 1):03d}", fy=0.36)


def sReason(r, im, d):
    panel(d, BG)
    photo(im, "hero", z=1.02 + 0.05 * r, fy=0.6)
    pill(d, C0, 540, 410, "진짜 이유", 60, YEL, INK, sc=kpop(r, 0.2))


def sCar(r, im, d):
    """Top view: the chair tries to turn inside a small car → can't."""
    panel(d, BG)
    v = photo(im, seq("turn", 48, r))
    if r > 1.4:
        badge(d, C0, *at(v, 0.8, 0.3), 64, RED, "x", kpop(r, 1.4, .22))
    pill(d, C0, 540, 410, "180도 회전 불가", 52, WHITE, INK, sc=kpop(r, 0.1))


def sInOut(r, im, d):
    panel(d, BG)
    v = photo(im, seq("inout", 40, r))
    if r < 1.45:
        pill(d, C0, 540, 410, "탈 땐 앞으로 ↑", 52, WHITE, INK, sc=kpop(r, 0.0))
    else:
        pill(d, C0, 540, 410, "내릴 땐 뒤로 ↓", 52, RED, WHITE, sc=kpop(r - 1.45, 0.0))


def sBlind(r, im, d):
    """His view: plain wall ahead, the door is behind his back."""
    panel(d, BG)
    photo(im, "pov_blind", z=1.0 + 0.04 * r)
    if r > 0.6:
        txt(d, C0, 540, 820, "?", 220 * kpop(r, 0.6, .22) + 1, YEL)
    pill(d, C0, 540, 410, "문이 열렸나…?", 52, WHITE, INK, sc=kpop(r, 0.1))


def sMirror(r, im, d):
    """Same view with the mirror: the door opening behind is visible."""
    panel(d, BG)
    photo(im, seq("pov", 26, r))
    if r > 1.5:
        badge(d, C0, 860, 470, 66, GREEN, "check", kpop(r, 1.5, .22))
    pill(d, C0, 540, 410, "거울로 뒤를 확인", 52, YEL, INK, sc=kpop(r, 0.1))


_PTS = None
def sLaw(r, im, d):
    """Back wall: the mirror starts 0.6 m above the floor."""
    global _PTS
    import json
    if _PTS is None:
        _PTS = json.load(open(os.path.join(R3D, "points.json")))
    panel(d, BG)
    v = photo(im, "law")
    k = ease((r - 0.3) / 0.8)
    if k > 0:
        x, yf = at(v, 0.33, _PTS["floor"][1]); _, ym = at(v, 0.33, _PTS["mirror_bottom"][1])
        y = lerp(yf, ym, k)
        d.line([cxy(C0, x, yf), cxy(C0, x, y)], fill=YEL + (255,), width=10)
        d.line([cxy(C0, x - 26, ym), cxy(C0, x + 26, ym)], fill=YEL + (255,), width=10)
        pill(d, C0, x + 170, (yf + ym) / 2, "0.6m 이상", 44, YEL, INK, sc=k)
    pill(d, C0, 540, 410, "장애인용 엘리베이터", 50, WHITE, INK, sc=kpop(r, 0.1))
    if r > 1.6:
        stamp(d, C0, 700, 600, "법으로 의무", r, 1.6, RED, 50)


def sTip(r, im, d):
    panel(d, BG)
    photo(im, "tip", z=1.0 + 0.03 * r, fy=0.55)
    if r > 1.0:
        badge(d, C0, 860, 470, 60, GREEN, "check", kpop(r, 1.0, .22))
    pill(d, C0, 540, 410, "거울 앞은 비워 주세요", 50, YEL, INK, sc=kpop(r, 0.1))


def sEnd(r, im, d):
    panel(d, BG)
    photo(im, "hook_b", z=1.08 - 0.02 * r)


SPOKEN = [
    "엘리베이터 탈 때 거울로 머리 만지죠? 구십구 퍼센트가 모르는, 진짜 용도가 있어요.",
    "진짜 이유는, 휠체어 때문이에요.",
    "좁은 엘리베이터에선, 휠체어가 안에서 돌 수가 없어요.",
    "그래서 탈 땐 앞으로, 내릴 땐 뒤로 나와야 하는데,",
    "등 뒤에 있는 문이, 열렸는지 안 보이잖아요.",
    "그때 거울로, 뒤를 보는 거예요.",
    "그래서 장애인용 엘리베이터엔, 뒷벽에 거울을 달도록 법으로 정해 놨어요.",
    "휠체어나 유모차가 타면, 거울 앞은 꼭 비워 주세요!",
    "알고 있었다, 몰랐다, 댓글로 알려 주세요!",
]
EMOTIONS = ["surprised", "excited", "explain", "explain", "secret", "amazed", "explain", "bright", "bright"]
BREATHS = (2, 5, 7)
LINES = [
    ("", None, None, sHook),
    ("", [("진짜 이유는", W_)], [("휠체어", Y_), (" 때문", W_)], sReason),
    ("", [("좁은 엘리베이터에선", W_)], [("안에서 못 돌아요", Y_)], sCar),
    ("", [("탈 땐 앞으로", W_)], [("내릴 땐 뒤로", Y_)], sInOut),
    ("", [("등 뒤의 문이", W_)], [("열렸는지 안 보여요", Y_)], sBlind),
    ("", [("그때 거울로", W_)], [("뒤를 확인", Y_)], sMirror),
    ("", [("장애인용 엘리베이터", W_)], [("뒷벽 거울", Y_), (" 법으로 의무", W_)], sLaw),
    ("", [("휠체어·유모차 타면", W_)], [("거울 앞 비워 주세요", Y_)], sTip),
    ("", [("알고 있었다 / 몰랐다", W_)], [("댓글", Y_), ("로 알려 주세요", W_)], sEnd),
]
T = (("엘리베이터 ", W_), ("거울", Y_), ("의 진짜 이유", W_))
Q = [[[("엘리베이터", W_)], [("거울", Y_)]], [[("99%가", Y_)], [("모르는 용도", W_)]]]
EV = lambda s: [("thud", 1.92, .4), ("ding", 1.95, 1320), ("pop", s[1] + .1, 800),
                ("no", s[2] + 1.4), ("whoosh", s[3] + .1), ("whoosh", s[3] + 1.35), ("pop", s[4] + .6, 900),
                ("ding", s[5] + 1.5, 1568), ("click", s[6] + .4), ("thud", s[6] + 1.6, .4), ("yes", s[7] + 1.3),
                ("pop", s[8] + .2, 1000)]
EP = build(20, "ep20", LINES, T, Q, EV, qsize=112, qys=(440, 560), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e20")
