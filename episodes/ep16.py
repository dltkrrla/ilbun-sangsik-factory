"""16편 - 맥주병은 왜 갈색일까 (내레이션판, 목소리 길이에 맞춰 장면 시간 계산)
VO 폴더: 환경변수 EP16_VO (기본 vo/ep16h = 직접 녹음, 없으면 vo/ep16tts)"""
import os, sys, json
from kit import *
import ep06 as o

BROWN = (122, 66, 26)
BROWN_HI = (168, 98, 44)
CLEAR = (214, 232, 240)
SUNC = (255, 200, 60)


def rel(fn, t0):
    return lambda t, im, d: fn(t - t0, im, d)


def beer(d, cam, x, y, s, col=BROWN, a=255, label=True):
    """Beer bottle, base at (x, y)."""
    c = col + (a,)
    rr(d, cam, x - 15 * s, y - 318 * s, x + 15 * s, y - 298 * s, 4, fill=(214, 178, 60, a))  # crown cap
    rr(d, cam, x - 13 * s, y - 300 * s, x + 13 * s, y - 210 * s, 5, fill=c)
    d.polygon([cxy(cam, x - 13 * s, y - 215 * s), cxy(cam, x + 13 * s, y - 215 * s), cxy(cam, x + 44 * s, y - 150 * s), cxy(cam, x - 44 * s, y - 150 * s)], fill=c)
    rr(d, cam, x - 44 * s, y - 156 * s, x + 44 * s, y, 14 * s, fill=c)
    rr(d, cam, x - 32 * s, y - 140 * s, x - 22 * s, y - 16 * s, 5, fill=(255, 255, 255, int(a * .28)))
    if label:
        rr(d, cam, x - 40 * s, y - 112 * s, x + 40 * s, y - 52 * s, 6, fill=(236, 214, 160, a))
        rr(d, cam, x - 40 * s, y - 112 * s, x + 40 * s, y - 100 * s, 0, fill=(200, 60, 50, a))


def sun(im, d, x, y, r, t, a=1.0):
    for i in range(12):
        ang = i * math.pi / 6 + t * 0.6
        L0, L1 = r * 0.95, r * (1.35 + 0.08 * math.sin(t * 6 + i))
        d.line([cxy(C0, x + math.cos(ang) * L0, y + math.sin(ang) * L0), cxy(C0, x + math.cos(ang) * L1, y + math.sin(ang) * L1)], fill=SUNC + (int(255 * a),), width=10)
    circ(d, C0, x, y, r, fill=SUNC + (int(255 * a),))


def ray(d, p, q, k, col=SUNC, w=9, dash=34):
    """Animated dashed ray from p to q; k = how far it has reached (0..1)."""
    x0, y0 = p; x1, y1 = q
    L = math.hypot(x1 - x0, y1 - y0); n = int(L * k / dash)
    for i in range(0, n, 2):
        a, b_ = i * dash / L, min((i + 1) * dash / L, k)
        d.line([cxy(C0, x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), cxy(C0, x0 + (x1 - x0) * b_, y0 + (y1 - y0) * b_)], fill=col + (255,), width=w)


def stink(d, x, y, t, a=255):
    for i in range(3):
        ph = (t * 0.9 + i / 3) % 1
        yy = y - ph * 160; xx = x + (i - 1) * 60
        pts = [cxy(C0, xx + 18 * math.sin((yy - k * 8) / 22 + t * 4), yy - k * 8) for k in range(12)]
        d.line(pts, fill=(150, 210, 90, int(a * (1 - ph))), width=9)


# ---------- scenes (r = seconds since the scene started) ----------
def sHook(r, im, d):
    panel(d, (44, 36, 30)); o.table(d)
    cam = (1.3 + 0.06 * r, 540, 800)
    for i, x in enumerate((360, 540, 720)):
        beer(d, cam, x, 1040, 1.55 if i == 1 else 1.3)
    rings(d, cam, 540, 790, 170, r)


def sSun(r, im, d):
    panel(d, (52, 60, 92)); o.table(d)
    beer(d, C0, 540, 1040, 1.5)
    sun(im, d, 830, 470, 70 * kpop(r, 0.05, .35), r)
    for i, (tx, ty) in enumerate(((500, 830), (540, 760), (580, 880))):
        ray(d, (790, 520), (tx, ty), ease((r - 0.3 - i * 0.1) / 0.5))
    pill(d, C0, 380, 430, "범인은 햇빛!", 68, YEL, INK, sc=kpop(r, 0.5))


def sHop(r, im, d):
    panel(d, (40, 70, 58))
    emo(im, 340, 700, 220 * kpop(r, 0.0, .3), "🌿", rot=6 * math.sin(r * 2))
    pill(d, C0, 340, 920, "홉 = 쓴맛", 62, WHITE, INK, sc=kpop(r, 0.35))
    sun(im, d, 800, 470, 60, r)
    ray(d, (760, 520), (440, 660), ease((r - 0.6) / 0.6))
    if r > 1.25:
        k = 0.5 + 0.5 * math.sin(r * 18)
        circ(d, C0, 360, 690, 120 + 14 * k, outline=(255, 230, 120, 200), width=6)


def sSkunk(r, im, d):
    panel(d, (54, 46, 70))
    emo(im, 540, 720, 300 * kpop(r, 0.0, .35), "🦨", flip=True)
    stink(d, 540, 560, r)
    if r > 0.9:
        pill(d, C0, 540, 1030, "일광취 日光臭", 78, YEL, INK, sc=kpop(r, 0.9, .3))


def sTiny(r, im, d):
    panel(d, (36, 44, 72))
    beer(d, C0, 300, 1080, 1.35)
    emo(im, 650, 640, 230 * kpop(r, 0.0, .3), "🔍", rot=-12 + 6 * math.sin(r * 3))
    k = kpop(r, 0.5, .35)
    if k > 0:
        txt(d, C0, 690, 900, "10억분의 1g", 92 * k, YEL)
        txt(d, C0, 690, 1000, "이것만 있어도 냄새", 52, WHITE, a=255 * ease((r - 0.9) / 0.3))


def sTest(r, im, d):
    panel(d, (60, 76, 108))
    # window
    rr(d, C0, 150, 360, 930, 1000, 18, fill=(150, 200, 240, 255), outline=(240, 240, 250, 255), width=14)
    d.line([cxy(C0, 540, 360), cxy(C0, 540, 1000)], fill=(240, 240, 250, 255), width=12)
    d.line([cxy(C0, 150, 680), cxy(C0, 930, 680)], fill=(240, 240, 250, 255), width=12)
    sun(im, d, 780, 500, 64, r)
    rr(d, C0, 120, 1000, 960, 1060, 8, fill=(230, 226, 214, 255))  # sill
    emo(im, 400, 900, 200, "🍺")
    # timer
    k = min(1, max(0, (r - 0.3) / 1.6))
    circ(d, C0, 760, 820, 92, fill=(255, 255, 255, 235))
    if k > 0:
        x0, y0 = cxy(C0, 760 - 80, 820 - 80); x1, y1 = cxy(C0, 760 + 80, 820 + 80)
        d.pieslice([x0, y0, x1, y1], -90, -90 + 360 * k, fill=RED + (255,))
    txt(d, C0, 760, 950, "30분", 72, WHITE)
    if r > 2.0:
        emo(im, 400, 700, 120 * kpop(r, 2.0, .3), "🤢")


def sShield(r, im, d):
    panel(d, (40, 52, 84)); o.table(d)
    sun(im, d, 540, 400, 62, r)
    k = ease((r - 0.15) / 0.6)
    # clear bottle: light passes
    beer(d, C0, 320, 1040, 1.3, CLEAR, a=210, label=False)
    ray(d, (500, 450), (320, 960), k)
    # brown bottle: light stops at the glass
    beer(d, C0, 760, 1040, 1.3)
    ray(d, (580, 450), (700, 800), k)
    if k >= 1:
        circ(d, C0, 700, 800, 22 + 6 * math.sin(r * 14), fill=(255, 240, 160, 200))
    badge(d, C0, 320, 600, 66, RED, "x", kpop(r, 0.8, .25))
    badge(d, C0, 760, 600, 66, GREEN, "check", kpop(r, 1.0, .25))


def sVs(r, im, d):
    panel(d, (40, 52, 84)); o.table(d)
    o.bottle(d, C0, 300, 1040, 1.35 * kpop(r, 0.0, .3) + 0.001, o.GREEN_G)
    beer(d, C0, 780, 1040, 1.45 * kpop(r, 0.15, .3) + 0.001)
    pill(d, C0, 300, 470, "마케팅", 68, GREEN, INK, sc=kpop(r, 0.35))
    pill(d, C0, 780, 470, "과학", 68, YEL, INK, sc=kpop(r, 1.2))
    txt(d, C0, 540, 760, "VS", 80, WHITE, a=255 * ease((r - 0.2) / .3))


def sEnd(r, im, d):
    panel(d, (44, 36, 30)); o.table(d)
    k = eio(r / 1.4); cam = (lerp(1.25, 1.0, k), 540, lerp(820, 760, k))
    for i, x in enumerate((360, 540, 720)):
        beer(d, cam, x, 1040, 1.55 if i == 1 else 1.3)
    rings(d, cam, 540, 790, 170, r + 3)


LINES = [  # (spoken text, caption l1, caption l2, scene)
    ("맥주병은 왜 전부 갈색일까요?", None, None, sHook),
    ("범인은 바로, 햇빛이에요.", [("범인은 바로", W_)], [("햇빛", Y_), ("이에요", W_)], sSun),
    ("맥주의 쓴맛을 내는 홉이 빛을 받으면,", [("쓴맛을 내는 홉이", W_)], [("빛을 받으면", Y_)], sHop),
    ("스컹크 냄새 같은 성분이 생겨요. 이걸 일광취라고 해요.", [("스컹크 냄새 성분이 생겨요", W_)], [("‘일광취’", Y_)], sSkunk),
    ("한 병에 십억 분의 일 그램만 있어도 냄새가 난대요.", [("한 병에", W_)], [("10억분의 1g", Y_), ("만 있어도", W_)], sTiny),
    ("투명한 잔에 담아 햇빛에 삼십 분만 둬도 맛이 변할 정도예요.", [("햇빛에", W_)], [("30분", Y_), ("이면 맛이 변해요", W_)], sTest),
    ("갈색 유리는 바로 이 빛을 막아 주는 거죠.", [("갈색 유리가", W_)], [("빛을 막아 줘요", Y_)], sShield),
    ("소주병은 마케팅, 맥주병은 과학이었네요.", [("소주병은 마케팅", W_)], [("맥주병은 과학!", Y_)], sVs),
    ("알고 있었다면, 댓글로 알려 주세요!", [("알고 있었다면", W_)], [("댓글", Y_), ("로 알려 주세요", W_)], sEnd),
]
T = (("맥주병은 왜 ", W_), ("갈색", Y_), ("일까?", W_))
Q = [[[("맥주병은", W_)], [("왜", W_)]], [[("전부", W_)], [("갈색?", Y_)]]]
GAP = 0.14

VO = os.environ.get("EP16_VO") or os.path.join(HERE, "vo", "ep16h")
if not os.path.exists(os.path.join(VO, "meta.json")):
    VO = os.path.join(HERE, "vo", "ep16tts")


def build_tts():
    os.makedirs(VO, exist_ok=True)
    meta = os.path.join(VO, "meta.json")
    if os.path.exists(meta):
        return json.load(open(meta))
    import tts_st
    durs = [tts_st.say(txt, os.path.join(VO, f"l{i:02d}.wav"), 1.0, 32)[0] for i, (txt, *_r) in enumerate(LINES)]
    json.dump(durs, open(meta, "w")); return durs


def trim(durs):
    import soundfile as sf, numpy as np
    out = []
    for i in range(len(durs)):
        x, sr = sf.read(os.path.join(VO, f"l{i:02d}.wav")); x = x if x.ndim == 1 else x.mean(1)
        idx = np.where(np.abs(x) > 0.02)[0]
        out.append((idx[0] / sr, idx[-1] / sr) if len(idx) else (0, durs[i]))
    return out


durs = build_tts(); spans = trim(durs)
starts, t = [], 0.15
for (a, e) in spans:
    starts.append(t - a); t = t - a + e + GAP
starts[1] = max(starts[1], 2.2)
for i in range(2, len(starts)):
    starts[i] = max(starts[i], starts[i - 1] + spans[i - 1][1] + GAP)
DUR = round(starts[-1] + spans[-1][1] + 1.0, 2)
seg = [max(0.0, s_ + spans[i][0] - 0.05) for i, s_ in enumerate(starts)]
seg[0] = 0.0
CAPS = [(seg[i], seg[i + 1] if i + 1 < len(seg) else DUR, l1, l2) for i, (_, l1, l2, _s) in enumerate(LINES) if l1]
SC_ = [(seg[i], rel(fn, seg[i])) for i, (*_x, fn) in enumerate(LINES)]
EV = [("pop", seg[1] + .5, 800), ("whoosh", seg[2] + .6), ("buzz", seg[3] + .1), ("ding", seg[3] + .9, 1568),
      ("pop", seg[4] + .5, 900), ("click", seg[5] + .3), ("no", seg[5] + 2.0), ("no", seg[6] + .8), ("yes", seg[6] + 1.0),
      ("pop", seg[7] + .35, 800), ("ding", seg[7] + 1.2, 1760)]
EP = Episode(16, T, None, None, SC_, CAPS, events=EV, dur=DUR, qhook=(Q, (585, 735), 120), qend=seg[1], cap_y=(1186, 1290))
EP.fit = 0.82; EP.end_y = 1100
CLIPS = [(starts[i], os.path.join(VO, f"l{i:02d}.wav")) for i in range(len(LINES))]

if __name__ == "__main__":
    print("VO", VO, "dur", DUR, "seg", [round(float(x), 2) for x in seg])
    if sys.argv[1] == "frames":
        for tt in sys.argv[2:]:
            EP.frame(float(tt)).save(f"sz/e16_{tt}.png")
    elif sys.argv[1] == "render":
        EP.render_voice(sys.argv[2], CLIPS)
