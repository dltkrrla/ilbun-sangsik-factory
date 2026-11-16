"""21편 - 수능 AI 안경: 쓰기만 해도 부정행위, 다음 해 응시 금지 + 반입 금지 물품·아날로그 시계
사실(교육부 2026.11.09 수험생 유의사항, korea.kr): AI 스마트안경·휴대전화·스마트워치·전자담배·블루투스 이어폰 등 모든 전자기기 반입 금지,
AI 안경은 시험 중 착용만 해도 사용 간주 → 시험 무효 + 다음 해 수능 응시 자격 박탈. 시계: 시침·분침 아날로그 중 결제·통신·LCD/LED 없는 것만
(평가원 2027 시행세부계획). 수능 2026-11-19(목). 실제 적발 사례의 개인은 언급하지 않는다."""
import math, os
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG = (52, 62, 98)


def ease(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


# ---------------- 3D photo layer (Blender renders, ../work/blender/r20) ----------------
R3D = os.environ.get("EP20_3D", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "blender", "r21"))
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



def has_flow():
    return os.path.exists(os.path.join(R3D, "flow_001.png"))


def sHook(r, im, d):
    """Real student (Flow clip) pushes up ordinary-looking glasses. No camera shown yet."""
    panel(d, BG)
    if has_flow():
        n = len([f for f in os.listdir(R3D) if f.startswith("flow_")])
        photo(im, f"flow_{min(n, int(r * 30) + 1):03d}", fy=0.44)
    else:
        photo(im, "orbit_000", z=1.0 + 0.03 * r)


_P = None
def pts(name):
    global _P
    if _P is None:
        import json
        _P = json.load(open(os.path.join(R3D, "points.json")))
    return _P[name]


def hud(im, x, y, w, h, k, label=None, big=None):
    """Glowing cyan AR display drawn inside a lens: scan frame + text (makes 'AI glasses' readable at a glance)."""
    if k <= 0:
        return
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
    cy = (0, 230, 255)
    x0, y0 = cxy(C0, x - w / 2, y - h / 2); x1, y1 = cxy(C0, x + w / 2, y + h / 2)
    dd.rounded_rectangle([x0, y0, x1, y1], 18, fill=(4, 20, 40, int(170 * k)), outline=cy + (int(240 * k),), width=6)
    im.alpha_composite(L)
    if label:
        txt(ImageDraw.Draw(im), C0, x, y - (h * 0.2 if big else 0), label, 42 if not big else 36, cy, a=255 * k)
    if big:
        txt(ImageDraw.Draw(im), C0, x, y + h * 0.12, big, 74, (255, 255, 255), a=255 * k)


def sReveal(r, im, d):
    panel(d, BG)
    name = seq("orbit", 30, r)
    v = photo(im, name)
    pill(d, C0, 540, 410, "평범한 안경…?", 52, WHITE, INK, sc=kpop(r, 0.1))
    if r > 1.2:
        k = ease((r - 1.2) / 0.3)
        for key in ("lensL", "lensR"):
            u, w_ = pts(name)[key]
            x, y = at(v, u, w_)
            hud(im, x, y, 190, 120, k, "AI")
        pill(d, C0, 540, 1130, "AI 안경", 64, RED, WHITE, sc=kpop(r, 1.3))


def sHow(r, im, d):
    panel(d, BG)
    if r < 1.6:
        photo(im, f"macro_{min(3, int(r / 0.4))}")
        if r > 0.8:
            pill(d, C0, 540, 410, "안경테 속 초소형 카메라", 48, YEL, INK, sc=kpop(r, 0.8))
    else:
        v = photo(im, "look", z=1.0 + 0.02 * (r - 1.6))
        pill(d, C0, 540, 410, "AI가 답을 알려 줌", 52, YEL, INK, sc=kpop(r, 1.6))
        k1 = ease((r - 1.8) / 0.3)
        u, w_ = pts("look")["lensL"]; hud(im, *at(v, u, w_), 340, 210, k1, "문제 촬영 중")
        if r > 2.4:
            u, w_ = pts("look")["lensR"]; hud(im, *at(v, u, w_), 330, 200, ease((r - 2.4) / 0.25), "AI 답", "정답 ③")


def sRule(r, im, d):
    panel(d, BG)
    photo(im, "orbit_029", z=1.04)
    pill(d, C0, 540, 410, "올해 수능", 52, WHITE, INK, sc=kpop(r, 0.1))
    if r > 0.9:
        stamp(d, C0, 540, 820, "쓰기만 해도 부정행위", r, 0.9, RED, 60)


def sPenalty(r, im, d):
    panel(d, BG)
    photo(im, "orbit_029", z=1.08, a=1.0)
    stamp(d, C0, 540, 650, "시험 무효", r, 0.2, RED, 70)
    if r > 1.0:
        pill(d, C0, 540, 950, "다음 해 수능도 응시 금지", 52, RED, WHITE, sc=kpop(r, 1.0))


# (u, v) of each item in the 'banned' render, X marks pop one by one
BANNED = [(0.22, 0.42, "휴대폰"), (0.5, 0.36, "스마트워치"), (0.8, 0.43, "무선 이어폰"), (0.36, 0.7, "전자담배")]
def sBanned(r, im, d):
    panel(d, BG)
    v = photo(im, "banned", z=1.0 + 0.02 * r)
    pill(d, C0, 540, 410, "전부 반입 금지", 52, RED, WHITE, sc=kpop(r, 0.1))
    for i, (u, w, name) in enumerate(BANNED):
        t0 = 0.5 + 0.55 * i
        if r > t0:
            x, y = at(v, u, w)
            badge(d, C0, x, y, 52, RED, "x", kpop(r, t0, .2))
            pill(d, C0, x, y + 78, name, 32, INK, WHITE, sc=kpop(r, t0, .2))


def sWatch(r, im, d):
    panel(d, BG)
    v = photo(im, "watches", z=1.0 + 0.02 * r)
    pill(d, C0, 540, 410, "시계는 아날로그만", 52, YEL, INK, sc=kpop(r, 0.1))
    if r > 0.8:
        badge(d, C0, *at(v, 0.3, 0.3), 60, GREEN, "check", kpop(r, 0.8, .2))
    if r > 1.4:
        badge(d, C0, *at(v, 0.7, 0.3), 60, RED, "x", kpop(r, 1.4, .2))
    if r > 2.2:
        pill(d, C0, 540, 1130, "통신·화면 기능 없는 것", 44, WHITE, INK, sc=kpop(r, 2.2))


def sShare(r, im, d):
    panel(d, BG)
    photo(im, "end", z=1.0 + 0.03 * r)
    pill(d, C0, 540, 410, "11월 19일(목) 수능", 52, YEL, INK, sc=kpop(r, 0.1))
    if r > 0.8:
        emo(im, 540, 820, 200 * kpop(r, 0.8, .25), "📲")


def sEnd(r, im, d):
    panel(d, BG)
    photo(im, "end", z=1.06 - 0.02 * r)
    rings(d, C0, 540, 820, 200, r)


SPOKEN = [
    "이 안경 쓰고 수능장 가면, 내년 수능까지 못 봐요.",
    "평범해 보여도, AI 안경일 수 있거든요.",
    "안경테에 숨은 카메라가 문제를 찍으면, AI가 답을 알려 줘요.",
    "그래서 올해 수능에선, 쓰기만 해도 부정행위예요.",
    "시험은 무효, 다음 해 수능도 못 봐요.",
    "휴대폰, 스마트워치, 무선 이어폰, 전자담배도 전부 반입 금지예요.",
    "시계는 바늘 있는 아날로그만, 통신이나 화면 기능이 없어야 해요.",
    "목요일에 수능 보는 친구한테, 꼭 보내 주세요!",
    "팔로우하면, 매일 하나씩 알려 드릴게요!",
]
EMOTIONS = ["steady"] * 9   # one consistent voice (user 11/16: changing tone per line breaks focus)
BREATHS = (2, 5, 7)
LINES = [
    ("", None, None, sHook),
    ("", [("평범해 보여도", W_)], [("AI 안경", Y_), ("일 수 있어요", W_)], sReveal),
    ("", [("숨은 카메라가 찍으면", W_)], [("AI가 답", Y_), ("을 알려 줘요", W_)], sHow),
    ("", [("올해 수능은", W_)], [("쓰기만 해도 부정행위", Y_)], sRule),
    ("", [("시험 무효", Y_)], [("다음 해 수능도 ", W_), ("응시 금지", Y_)], sPenalty),
    ("", [("휴대폰·스마트워치", W_)], [("이어폰·전자담배 ", W_), ("반입 금지", Y_)], sBanned),
    ("", [("시계는 ", W_), ("아날로그", Y_), ("만", W_)], [("통신·화면 기능 없이", W_)], sWatch),
    ("", [("목요일 수능 보는 친구에게", W_)], [("꼭 보내 주세요", Y_)], sShare),
    ("", [("팔로우하면", W_)], [("매일 하나씩", Y_), (" 1분 상식", W_)], sEnd),
]
T = (("수능 ", W_), ("AI 안경", Y_), (" 쓰면?", W_))
Q = [[[("이 안경 쓰면", W_)]], [[("내년 수능까지", Y_)], [("못 봐요", W_)]]]
EV = lambda s: [("pop", s[1] + 1.3, 900), ("click", s[2] + 0.8), ("ding", s[2] + 2.1, 1320),
                ("thud", s[3] + 0.9, .4), ("no", s[3] + 0.95), ("thud", s[4] + 0.2, .4), ("no", s[4] + 1.0),
                ("no", s[5] + 0.5), ("no", s[5] + 1.05), ("no", s[5] + 1.6), ("no", s[5] + 2.15),
                ("yes", s[6] + 0.8), ("no", s[6] + 1.4), ("pop", s[7] + 0.8, 1000), ("pop", s[8] + 0.2, 1000)]
EP = build(21, "ep21", LINES, T, Q, EV, qsize=98, qys=(1070, 1180), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e21")
