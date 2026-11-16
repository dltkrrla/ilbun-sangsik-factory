"""22편 - 수능 끝! 수험표 버리면 안 돼요, 팔면 더 안 돼요 (수험생 할인 + 수험표 거래 주의)
사실: 2027학년도 수험생 할인(2026.11 보도) — 코엑스 아쿠아리움 본인 50%(11/19~12/18), 레고랜드 본인 40%, 롯데월드 종합이용권 27,000원,
이스타항공 국내선 25%·국제선 최대 10%(수험생+동반 1인). 수험표+신분증 제시. 타인 수험표로 할인받으면 사기죄 대상, 사진 교체는 공문서 위조
(서울신문 2018, MBC 보도 인용 기사), 경찰청: 수험표 게시·대여·매매 금지(보안뉴스 2024). 업체명은 말하지 않고 종류로만 말한다."""
import math, os
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main

BG = (52, 62, 98)


def ease(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


# ---------------- 3D photo layer (Blender renders, ../work/blender/r20) ----------------
R3D = os.environ.get("EP20_3D", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "blender", "r22"))
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



_P = None
def pts(name):
    global _P
    if _P is None:
        import json
        _P = json.load(open(os.path.join(R3D, "points.json")))
    return _P[name]


def P(v, name, key):
    u, w = pts(name)[key]
    return at(v, u, w)


def has_flow():
    return os.path.exists(os.path.join(R3D, "flow_001.png"))


def sHook(r, im, d):
    """Real student (Flow clip) about to throw the ticket away."""
    panel(d, BG)
    if has_flow():
        n = len([f for f in os.listdir(R3D) if f.startswith("flow_")])
        photo(im, f"flow_{min(n, int(r * 30) + 1):03d}", fy=0.62)
    else:
        photo(im, "card", z=1.0 + 0.03 * r)


def sCoupon(r, im, d):
    panel(d, BG)
    v = photo(im, "card", z=1.0 + 0.04 * r)
    x, y = P(v, "card", "card")
    pill(d, C0, 540, 410, "수험표", 56, WHITE, INK, sc=kpop(r, 0.1))
    if r > 0.9:
        stamp(d, C0, x, y, "할인 쿠폰", r, 0.9, RED, 70)


def sBenefit(r, im, d):
    panel(d, BG)
    v = photo(im, "benefit", z=1.0 + 0.02 * r)
    pill(d, C0, 540, 410, "2026년 11월 기준 · 수험생 본인", 40, WHITE, INK, sc=kpop(r, 0.1))
    for i, (key, lab, col) in enumerate((("t0", "롯데월드 27,000원", YEL), ("t1", "코엑스 아쿠아리움 50%", YEL), ("t2", "레고랜드 40%", YEL))):
        t0 = 0.3 + 1.9 * i
        if r > t0:
            x, y = P(v, "benefit", key)
            x = (300, 540, 790)[i]; y = (y + 150, y - 30, y + 150)[i]
            pill(d, C0, x, y - (60 if i == 1 else 80) + (150 if i != 1 else 0) * 0, lab, 34, col, INK, sc=kpop(r, t0, .2))


def sFly(r, im, d):
    panel(d, BG)
    v = photo(im, "fly", z=1.0 + 0.03 * r)
    pill(d, C0, 540, 410, "비행기표도", 52, WHITE, INK, sc=kpop(r, 0.1))
    if r > 0.9:
        x, y = P(v, "fly", "bp")
        pill(d, C0, 540, y - 90, "이스타항공 국내선 25%", 46, YEL, INK, sc=kpop(r, 0.6))


def sSell(r, im, d):
    panel(d, BG)
    v = photo(im, "sell", z=1.0 + 0.03 * r)
    x, y = P(v, "sell", "phone")
    pill(d, C0, 540, 410, "중고 거래", 52, WHITE, INK, sc=kpop(r, 0.1))
    if r > 0.5:
        pill(d, C0, x - 40, y + 30, "수험표 팝니다", 34, INK, WHITE, sc=kpop(r, 0.5, .2))
    if r > 1.3:
        badge(d, C0, x - 40, y - 90, 80, RED, "x", kpop(r, 1.3, .22))


def sFraud(r, im, d):
    panel(d, BG)
    v = photo(im, "sell", z=1.1)
    pill(d, C0, 540, 410, "남의 수험표로 할인받으면", 46, WHITE, INK, sc=kpop(r, 0.1))
    if r > 1.0:
        stamp(d, C0, 540, 800, "사기죄", r, 1.0, RED, 96)


def sForge(r, im, d):
    panel(d, BG)
    name = seq("swap", 16, r)
    v = photo(im, name)
    pill(d, C0, 540, 410, "사진 바꿔 붙이면", 50, WHITE, INK, sc=kpop(r, 0.1))
    if r > 1.4:
        x, y = P(v, name, "card")
        stamp(d, C0, x + 60, y, "공문서 위조", r, 1.4, RED, 70)


def sTip(r, im, d):
    panel(d, BG)
    v = photo(im, "ids", z=1.0 + 0.02 * r)
    pill(d, C0, 540, 410, "수험표 + 신분증", 52, YEL, INK, sc=kpop(r, 0.1))
    for i, key in enumerate(("card", "id")):
        t0 = 0.5 + 0.5 * i
        if r > t0:
            x, y = P(v, "ids", key)
            badge(d, C0, x, y - 60, 56, GREEN, "check", kpop(r, t0, .2))
    if r > 2.2:
        pill(d, C0, 540, 1130, "수험표 사진 SNS 금지", 46, RED, WHITE, sc=kpop(r, 2.2))


def sEnd(r, im, d):
    panel(d, BG)
    photo(im, "end", z=1.06 - 0.01 * r)
    if r > 0.4:
        emo(im, 540, 800, 190 * kpop(r, 0.4, .25), "📲")
    if r > 2.2:
        rings(d, C0, 540, 800, 200, r)


SPOKEN = [
    "수능 끝나고 수험표 버리면 안 돼요. 그리고 팔면, 더 안 돼요.",
    "수험표가, 할인 쿠폰이거든요.",
    "롯데월드는 이만 칠천 원, 코엑스 아쿠아리움은 반값, 레고랜드는 사십 퍼센트 할인이에요.",
    "이스타항공은, 국내 노선이 이십오 퍼센트 할인이에요.",
    "그런데 이 수험표, 중고로 팔면 안 돼요.",
    "남의 수험표로 할인받으면, 사기죄가 될 수 있어요.",
    "사진까지 바꿔 붙이면, 공문서 위조예요.",
    "수험표랑 신분증을 같이 챙기고, 사진은 SNS에 올리지 마세요.",
    "수능 본 친구한테 보내 주세요! 팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (2, 5, 7)
LINES = [
    ("", None, None, sHook),
    ("", [("수험표가", W_)], [("할인 쿠폰", Y_), ("이에요", W_)], sCoupon),
    ("", [("놀이공원·아쿠아리움", W_)], [("최대 50%", Y_), (" 할인", W_)], sBenefit),
    ("", [("이스타항공", W_)], [("국내선 25%", Y_), (" 할인", W_)], sFly),
    ("", [("그런데 수험표", W_)], [("중고로 팔면 안 돼요", Y_)], sSell),
    ("", [("남의 수험표로 할인받으면", W_)], [("사기죄", Y_), ("가 될 수 있어요", W_)], sFraud),
    ("", [("사진을 바꿔 붙이면", W_)], [("공문서 위조", Y_)], sForge),
    ("", [("수험표 + 신분증", Y_), (" 같이", W_)], [("사진은 SNS에 올리지 않기", W_)], sTip),
    ("", [("수능 본 친구에게 보내 주세요", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)], sEnd),
]
T = (("수험표", Y_), (" 버리지 마세요", W_))
Q = [[[("수험표", Y_)], [("버리면 안 돼요", W_)]], [[("팔면", Y_)], [("더 안 돼요", W_)]]]
EV = lambda s: [("thud", s[1] + 0.9, .4), ("ding", s[1] + 0.95, 1320), ("pop", s[2] + 0.3, 900), ("pop", s[2] + 2.2, 1000),
                ("pop", s[2] + 4.1, 1100), ("whoosh", s[3] + 0.1), ("ding", s[3] + 0.6, 1568), ("pop", s[4] + 0.5, 800),
                ("no", s[4] + 1.3), ("thud", s[5] + 1.0, .4), ("no", s[5] + 1.05), ("thud", s[6] + 1.4, .4), ("no", s[6] + 1.45),
                ("yes", s[7] + 0.5), ("yes", s[7] + 1.0), ("no", s[7] + 2.2), ("pop", s[8] + 0.4, 1000)]
EP = build(22, "ep22", LINES, T, Q, EV, qsize=98, qys=(440, 550), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e22")
