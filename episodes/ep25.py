"""25편 - 동전 옆면 톱니는 왜 있을까 (전부 3D, 사람 없음 — 사용자: "우리가 모르고 있던 내용, 볼펜 뚜껑 구멍 같은 것")
사실: 50원 109개·100원 110개·500원 120개, 10원 이하는 민무늬. 금·은화를 조금씩 갉아 모으는 것을 막으려고 톱니를 넣음
(한국은행 '주화 이야기' https://www.bok.or.kr/portal/bbs/B0000219/view.do?menuNo=200148&nttId=236078).
뉴턴: 1696년 영국 대개주(Great Recoinage) 때 왕립 조폐국 감사(Warden)로 일하며 깎는 사람·위조범을 직접 추적 (챌로너 1699년 처형). 톱니 기술은 프랑스인 블롱도가 먼저 만들었고 대개주는 뉴턴 부임(1696-03) 전에 시작됨 (newtonandthemint.history.ox.ac.uk) (Wikipedia Reeding, rd.com).
톱니 자체는 뉴턴 이전에도 있었으므로 "뉴턴이 발명"이라고 하지 않는다. 소액 동전은 비용 절감으로 민무늬(위키트리 2026-05).
실험(플레이북 L14): 약 30초 + 15초쯤 두 번째 반전(뉴턴)."""
import math, os
from PIL import Image, ImageDraw
from kit import *
from vtl import build, main
from sangsik2 import F

BG = (30, 36, 64)


def ease(k):
    k = max(0.0, min(1.0, k)); return k * k * (3 - 2 * k)


# ---------------- 3D photo layer (Blender renders, ../work/blender/r20) ----------------
R3D = os.environ.get("EP20_3D", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "work", "blender", "r25"))
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




def spin(r):
    return f"spin_{int(r * FPS3D) % 20:03d}"


def ring(im, x, y, rad, k, col=(235, 60, 50)):
    if k <= 0:
        return
    L = Image.new("RGBA", im.size, (0, 0, 0, 0)); dd = ImageDraw.Draw(L)
    X, Y = cxy(C0, x, y); R_ = rad * C0[0] * SC * (1.5 - 0.5 * min(1, k)); w = max(3, int(12 * C0[0] * SC))
    dd.ellipse([X - R_, Y - R_, X + R_, Y + R_], outline=col + (int(255 * min(1, k * 2)),), width=w)
    im.alpha_composite(L)


def sHook(r, im, d):
    panel(d, BG)
    photo(im, spin(r), z=1.0 + 0.1 * ease(r / 0.5))


def sCount(r, im, d):
    panel(d, BG)
    v = photo(im, "three", z=1.0)
    for i, (key, n, t0) in enumerate((("c500", "120개", 0.15), ("c100", "110개", 1.5), ("c50", "109개", 2.1))):
        x, y = P(v, "three", key)
        pill(d, C0, x, max(y - 70, 360), n, 50, YEL if i == 0 else WHITE, INK, sc=kpop(r, t0))
    for key, n in (("b500", "500원"), ("b100", "100원"), ("b50", "50원")):
        x, y = P(v, "three", key)
        pill(d, C0, x, y + 60, n, 36, INK, WHITE, sc=kpop(r, 0.05))


def sThief(r, im, d):
    panel(d, BG)
    photo(im, "clip_000", z=1.0 + 0.05 * r)
    pill(d, C0, 540, 410, "옛날 금화", 46, YEL, INK, sc=kpop(r, 0.6))
    stamp(d, C0, 540, 1120, "도둑 때문", r, 0.9, RED, 78)


def sClip(r, im, d):
    panel(d, BG)
    i = min(5, int(r / 0.6))
    v = photo(im, f"clip_{i:03d}", z=1.05)
    pill(d, C0, 540, 410, "가장자리를 몰래 깎아서", 46, WHITE, INK, sc=kpop(r, 0.1))
    if i >= 2:
        x, y = P(v, f"clip_{i:03d}", "pile")
        pill(d, C0, min(x - 20, 760), y + 110, "금가루 모아 팔기", 44, YEL, INK, sc=kpop(r, 1.3))


def sReed(r, im, d):
    panel(d, BG)
    if r < 1.5:
        photo(im, "reed_a", z=1.0 + 0.04 * r)
        pill(d, C0, 540, 410, "옆면에 톱니를 새기면", 48, YEL, INK, sc=kpop(r, 0.1))
    else:
        v = photo(im, "reed_b", z=1.06)
        x, y = P(v, "reed_b", "flat")
        ring(im, x, y, 150, (r - 1.6) / 0.3)
        pill(d, C0, 540, 1140, "깎은 자리가 바로 보임", 50, RED, WHITE, sc=kpop(r, 1.9))


def sNewton(r, im, d):
    panel(d, BG)
    v = photo(im, "newton", z=1.0 + 0.04 * r)
    pill(d, C0, 540, 410, "사과의 그 뉴턴", 52, YEL, INK, sc=kpop(r, 0.9))
    pill(d, C0, 540, 1140, "1696년 영국 조폐국", 44, WHITE, INK, sc=kpop(r, 1.6))


def sSwap(r, im, d):
    panel(d, BG)
    v = photo(im, "swap", z=1.0 + 0.03 * r)
    x, y = P(v, "swap", "old"); pill(d, C0, max(x, 300), max(y - 190, 400), "깎인 옛 동전", 44, WHITE, INK, sc=kpop(r, 0.2))
    x, y = P(v, "swap", "new"); pill(d, C0, min(x, 800), max(y - 200, 400), "톱니 새 동전", 44, YEL, INK, sc=kpop(r, 1.2))
    stamp(d, C0, 540, 1130, "위조범도 직접 추적", r, 3.0, RED, 60)


def sTen(r, im, d):
    panel(d, BG)
    v = photo(im, "ten", z=1.04)
    x, y = P(v, "ten", "c10"); pill(d, C0, x, max(y - 70, 400), "매끈", 50, YEL, INK, sc=kpop(r, 0.2))
    x, y = P(v, "ten", "c500"); pill(d, C0, min(x, 880), max(y - 70, 400), "톱니", 50, WHITE, INK, sc=kpop(r, 0.5))
    pill(d, C0, 540, 1150, "값이 낮아 굳이 안 새김", 46, WHITE, INK, sc=kpop(r, 1.4))


def sEnd(r, im, d):
    panel(d, BG)
    photo(im, spin(r), z=1.1)
    if r > 0.4:
        emo(im, 800, 560, 170 * kpop(r, 0.4, .25), "📲")


SPOKEN = [
    "동전에 있는 줄무늬, 이거 왜 있는지 궁금하지 않았나요?",
    "오백 원은 정확히 백이십 개, 백 원은 백십 개.",
    "진짜 이유는, 도둑 때문이에요.",
    "옛날 동전은 진짜 금과 은이라, 가장자리를 몰래 깎아 팔았거든요.",
    "톱니를 새기면, 조금만 깎아도 바로 티가 나요.",
    "이 일을 맡은 사람이, 사과로 유명한 뉴턴이에요.",
    "영국 조폐국에서 옛동전을 톱니동전으로 싹 바꾸고, 위조범까지 직접 잡았죠.",
    "십 원이 매끈한 이유요? 값이 낮아서, 굳이 안 새긴 거예요.",
    "동전 모으는 친구에게 보내 주세요! 팔로우하면, 매일 하나씩 알려 드릴게요.",
]
EMOTIONS = ["steady"] * 9
BREATHS = (3, 6)
LINES = [
    ("", None, None, sHook),
    ("", [("500원", Y_), ("은 정확히 ", W_), ("120개", Y_)], [("100원은 110개", W_)], sCount),
    ("", [("진짜 이유는", W_)], [("도둑", Y_), (" 때문이에요", W_)], sThief),
    ("", [("옛날 동전은 진짜 ", W_), ("금과 은", Y_)], [("가장자리를 몰래 깎아 팔았죠", W_)], sClip),
    ("", [("톱니", Y_), ("를 새기면", W_)], [("조금만 깎아도 바로 티가 나요", W_)], sReed),
    ("", [("이 일을 맡은 사람이", W_)], [("사과로 유명한 ", W_), ("뉴턴", Y_)], sNewton),
    ("", [("옛 동전을 ", W_), ("톱니 동전", Y_), ("으로", W_)], [("싹 바꾸고, ", W_), ("위조범", Y_), ("까지 잡았죠", W_)], sSwap),
    ("", [("10원", Y_), ("이 매끈한 이유?", W_)], [("값이 낮아 굳이 안 새긴 것", W_)], sTen),
    ("", [("동전 모으는 친구에게 보내요", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)], sEnd),
]
T = (("동전 톱니", Y_), ("의 비밀", W_))
Q = [[[("동전에 있는 ", W_), ("줄무늬", Y_)]], [[("왜 있을까요?", Y_)]]]
EV = lambda s: [("pop", s[1] + 0.15, 700), ("pop", s[1] + 1.5, 800), ("pop", s[1] + 2.1, 900), ("thud", s[2] + 0.9, .4),
                ("whoosh", s[3] + 0.1), ("pop", s[3] + 1.3, 900), ("pop", s[4] + 0.1, 800), ("no", s[4] + 1.6), ("thud", s[4] + 1.9, .4),
                ("ding", s[5] + 0.9, 1320), ("pop", s[6] + 0.2, 800), ("pop", s[6] + 1.2, 900), ("thud", s[6] + 3.0, .4), ("pop", s[7] + 0.2, 800), ("pop", s[8] + 0.4, 1000)]
EP = build(25, "ep25", LINES, T, Q, EV, qsize=98, qys=(1070, 1180), spoken=SPOKEN, emotions=EMOTIONS, breaths=BREATHS)
if __name__ == "__main__":
    main(EP, "e25")
