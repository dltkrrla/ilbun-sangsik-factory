"""16편 리메이크(맥주병은 왜 갈색): 아저씨 연기 클립 + 설계도 모션그래픽 위 투명 오버레이 + 소리.
사실: Cook's Illustrated(10억분의 1g/12온스, 투명 잔 햇빛 창가 30분 → 이취), Science News(갈색 유리 500nm 아래 차단), ASBC(3-MBT 역치 수 ng/L).
usage: python3 ep16r.py audio out.wav | overlay out.webm | stills name t1 t2 ..."""
import os, sys, json, math, subprocess, wave
os.environ.setdefault("SIG", "B")
import numpy as np
from PIL import Image, ImageDraw
import sangsik2 as b
from sangsik2 import *

VO = "/home/claude/work/vo16r"
VOD = json.load(open(f"{VO}/meta.json"))
NB = [0.0]
for d in VOD:
    NB.append(NB[-1] + d + 0.45)
DUR = NB[-1]
b.DUR = DUR
b.EP_TITLE = ((" ", WHITE),)
RED = (235, 70, 50)
Q_HOLD = 1.5                      # 여는 질문이 가운데 크게 머무는 시간 → 이후 아래로 내려가 자막 자리로
Q_ROWS = [[[("맥주병은", WHITE)], [("왜 하나같이", WHITE)]], [[("갈색", YEL), ("일까요?", WHITE)]]]
Q_HIT = [0.12, 0.80, 1.45]   # 말하는 박자에 맞춘 단어별 '쾅'


TITLE_TAG, TITLE_BIG = "10명 중 9명은 모르는", "맥주병 갈색의 비밀"
T_IN, T_OUT = 0.15, 2.0              # 위쪽 큰 제목: 0.15초에 등장, 2초에 퇴장 (참고 영상의 '제목 후킹')


def hook_title(im, t):
    if not (T_IN <= t < T_OUT + 0.2):
        return
    a = ease((t - T_IN) / 0.08) * (1 - ease((t - T_OUT) / 0.2))
    k = back((t - T_IN) / 0.28)
    tag = box_img(TITLE_TAG, 48, (226, 52, 44), WHITE, pad=30)
    put(im, tag, 540, 238, a, 0.7 + 0.3 * k)
    big = line_img(((TITLE_BIG, WHITE),), 126)
    put(im, big, 540, 360, a, (0.6 + 0.4 * back((t - T_IN - 0.06) / 0.3)) * (1 + 0.015 * math.sin(t * 7)))
    # 머리 위 '??' 낙서 스티커 (0.9초)
    if t >= 0.9:
        kk = back((t - 0.9) / 0.25)
        q = line_img((("??", YEL),), 120).rotate(-12, expand=True, resample=Image.BICUBIC)
        put(im, q, 820, 640, ease((t - 0.9) / 0.1) * (1 - ease((t - T_OUT) / 0.2)), (0.5 + 0.5 * kk) * (1 + 0.06 * math.sin(t * 10)))


def hook_question(im, t, t_end):
    """여는 질문: 화면 가운데 한 단어씩 쾅 → '꽃 모양' 밑줄 → 아래 자막 자리로 미끄러져 내려가며 작아짐."""
    if t >= t_end:
        return
    size = 96; f = F(size); tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    ys = [1290, 1425]                  # 움직이지 않고 한자리에 (위쪽은 꽃 모양 바닥이 나올 자리)
    scl = 1.0
    a_out = 1 - ease((t - (t_end - 0.12)) / 0.12)
    idx = 0
    for words, cy in zip(Q_ROWS, ys):
        ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) * scl for w in words]
        sp = size * 0.26 * scl; x = 540 - (sum(ws) + sp * (len(ws) - 1)) / 2
        for w, ww in zip(words, ws):
            lt = t - Q_HIT[idx]; idx += 1
            if lt >= 0:
                sc = scl * (1 + 0.9 * (1 - ease(lt / 0.17)))
                yel = any(c == YEL for _, c in w)
                if yel:
                    sc *= 1 + 0.05 * math.sin(t * 15)
                    k = ease((t - 1.6) / 0.2)                      # '갈색' 밑줄 쓱
                    if k > 0:
                        d = ImageDraw.Draw(im)
                        d.rounded_rectangle((x + 6, cy + 66 * scl, x + 6 + (ww - 12) * k, cy + 80 * scl), 7, fill=YEL + (int(255 * a_out),))
                put(im, line_img(tuple(w), size), x + ww / 2, cy, ease(lt / 0.07) * a_out, sc)
            x += ww + sp
Y_, W_ = YEL, WHITE
CAPS = [
    None,
    ([("범인은 바로", W_)], [("햇빛", Y_), ("이에요", W_)]),
    ([("쓴맛을 내는 ", W_), ("홉", Y_), ("이", W_)], [("빛을 받으면", Y_)]),
    ([("스컹크 냄새 성분이 생겨요", W_)], [("‘일광취’", Y_)]),
    ([("한 병에", W_)], [("10억분의 1g", Y_), ("만 있어도", W_)]),
    ([("투명한 잔 + 햇빛", W_)], [("30분", Y_), ("이면 맛이 변해요", W_)]),
    ([("갈색 유리가", W_)], [("빛을 막아 줘요", Y_)]),
    ([("맥주는", W_)], [("햇빛 안 드는 곳", Y_), ("에 두세요", W_)]),
    ([("친구에게 알려 주세요!", W_)], [("팔로우", Y_), ("하면 매일 하나씩", W_)]),
]


def grad_layer():
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = np.zeros((H, W), np.uint8)
    for y in range(H):
        a[y, :] = int(min(230, max(0.0, 1 - y / 330) * 150 + max(0.0, (y - 1180) / (H - 1180)) ** 1.2 * 200))
    g.putalpha(Image.fromarray(a)); return g


GRAD = grad_layer()


def pop(im, t, t0, img, x, y):
    if t >= t0:
        put(im, img, x, y, ease((t - t0) / 0.12), 0.7 + 0.3 * back((t - t0) / 0.25))


def overlay(t):
    im = GRAD.copy()
    signature2(im, t)
    hook_title(im, t)
    s = NB
    # 0: 첫 문장 + 큰 5
    if t < s[1]:
        hook_question(im, t, s[1])
    if t >= s[8]:
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1252, 1.0, 0.6 + 0.4 * back((t - s[8]) / 0.28))
    for i in range(1, len(CAPS)):
        t0, t1 = s[i], s[i + 1]
        if t0 <= t < t1:
            l1, l2 = CAPS[i]
            a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if i < len(CAPS) - 1 else 1
            for j, (segs, cy) in enumerate(((l1, 1388), (l2, 1500))):
                lt = t - t0 - j * 0.13
                if lt >= 0:
                    put(im, line_img(tuple(segs)), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
    return im


def audio(path):
    import soundfile as sf
    sr = 44100; n = int(DUR * sr); x = np.zeros(n); rng = np.random.default_rng(3)
    def add(at, sig):
        i = int(at * sr); sig = sig[: max(0, n - i)]; x[i:i + len(sig)] += sig
    def env(m, dd): return np.exp(-np.arange(m) / sr / dd)
    def popf(at, f0=700, vol=.2):
        m = int(.12 * sr); tt = np.arange(m) / sr; add(at, vol * np.sin(2 * np.pi * (f0 + 380 * np.exp(-tt * 40)) * tt) * env(m, .03))
    def whoosh(at, ln=.38, vol=.18):
        m = int(ln * sr); z = rng.standard_normal(m); y = np.zeros(m); s_ = 0.0; a = np.linspace(.02, .35, m)
        for i in range(m):
            s_ += a[i] * (z[i] - s_); y[i] = s_
        add(max(0, at - ln * .6), vol * 3 * y * np.sin(np.pi * np.arange(m) / m) ** 2)
    def thud(at, vol=.4):
        m = int(.25 * sr); tt = np.arange(m) / sr
        add(at, vol * np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-tt * 30)) / sr) * env(m, .07))
    def ding(at, f=1320, vol=.16):
        m = int(.7 * sr); tt = np.arange(m) / sr; add(at, vol * (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.01 * tt)) * env(m, .22))
    s = NB
    whoosh(0.16, .25, .16); popf(T_IN + 0.02, 980, .2); popf(0.92, 1200, .18)   # 컷·제목·??
    for k_, th in enumerate(Q_HIT):
        thud(th, .32) if k_ in (0, 2) else popf(th, 820, .15)
    whoosh(Q_HOLD + 0.2, .3, .12)
    for i in range(1, len(s) - 1):
        whoosh(s[i]); popf(s[i] + 0.05, 820, .16)
    popf(s[1] + 0.91, 1000, .2)                          # 자외선·파란 빛
    thud(s[2] + 1.57, .3); popf(s[2] + 1.86, 900, .18)   # 쪼개짐
    thud(s[4] + 2.15, .35); ding(s[4] + 2.19, 1320)      # 10억분의 1g
    ding(s[5] + 2.55, 990)                               # 30분
    thud(s[6] + 1.13, .4); popf(s[6] + 1.57, 900, .18)   # 막았다
    ding(s[8], 1319); ding(s[8] + 0.14, 1760)
    x *= 0.55
    for i in range(len(VOD)):
        v, vsr = sf.read(f"{VO}/l{i:02d}.wav")
        if v.ndim > 1: v = v.mean(1)
        if vsr != sr: v = np.interp(np.arange(int(len(v) * sr / vsr)) * vsr / sr, np.arange(len(v)), v)
        st = int((s[i] + 0.12) * sr); v = v[: max(0, n - st)]; x[st:st + len(v)] += 0.95 * v / max(1e-6, np.abs(v).max())
    x = np.tanh(x * 1.1) * .95
    tmp = path + ".sfx.wav"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes())
    fo = DUR - 0.8
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", f"{OUT}/music/theme.wav", "-i", tmp,
                    "-filter_complex", f"[0:a]atrim=0:{DUR},volume=-17dB,afade=t=in:d=0.05,afade=t=out:st={fo}:d=0.8[m];[m][1:a]amix=inputs=2:normalize=0[a]",
                    "-map", "[a]", "-ar", "44100", "-ac", "2", "-t", str(DUR), path], check=True)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "stills":
        ims = []
        for v in sys.argv[3:]:
            bg = Image.new("RGBA", (W, H), (120, 110, 95, 255)); bg.alpha_composite(overlay(float(v)))
            ims.append(bg.convert("RGB").resize((360, 640), Image.LANCZOS))
        st = Image.new("RGB", (360 * len(ims), 640))
        for i, x in enumerate(ims):
            st.paste(x, (i * 360, 0))
        st.save(f"{OUT}/{sys.argv[2]}.jpg", quality=88)
    elif mode == "audio":
        audio(sys.argv[2]); print("ok", sys.argv[2], DUR, [round(v, 2) for v in NB])
    else:
        out = sys.argv[2]; tmp = out + ".part.webm"
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-deadline", "realtime", "-cpu-used", "8",
                              "-row-mt", "1", "-auto-alt-ref", "0", tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(overlay(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, out); print("ok", out)
