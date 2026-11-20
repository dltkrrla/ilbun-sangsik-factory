"""31편 실사판: 탄산음료 페트병 바닥이 꽃 모양인 이유. AI 사진·영상 배경(샌드박스 합성) 위에 얹을 투명 오버레이 + 소리.
사실: 꽃잎형(petaloid) 바닥, 대개 다리 5개(특허: 3~7개, 5개가 바람직) · 탄산 병 속 압력 5~7기압(vienna.at, Alpla) ·
다리가 힘을 나눠 바닥이 불룩해지는 것을 막고 가벼운 병이 서게 함 · 생수병은 압력이 낮아 평평한 바닥 ·
옛 탄산 페트병은 반구형 바닥 + 따로 붙인 폴리에틸렌 받침(US5850932 배경 설명).
usage: python3 ep31r.py audio out.wav | overlay out.webm | stills name t1 t2 ..."""
import os, sys, json, math, subprocess, wave
os.environ.setdefault("SIG", "B")
import numpy as np
from PIL import Image, ImageDraw
import sangsik2 as b
from sangsik2 import *

VO = "/home/claude/work/vo31b"
VOD = json.load(open(f"{VO}/meta.json"))
NB = [0.0]
for d in VOD:
    NB.append(NB[-1] + d + 0.45)
DUR = NB[-1]
b.DUR = DUR
b.EP_TITLE = ((" ", WHITE),)
RED = (235, 70, 50)
Y_, W_ = YEL, WHITE
CAPS = [
    None,
    ([("생수병 바닥은 ", W_), ("평평", Y_), ("한데", W_)], [("탄산음료 병만 ", W_), ("꽃 모양", Y_)]),
    ([("만약 바닥이 ", W_), ("평평", Y_), ("하면?", W_)], [("불룩", Y_), (" 튀어나와 넘어져요", W_)]),
    ([("범인은 바로 ", W_), ("병 속 압력", Y_)], [("무려 ", W_), ("5~7기압", Y_)]),
    ([("다리 ", W_), ("5개", Y_), ("가 힘을 나눠", W_)], [("병을 ", W_), ("똑바로", Y_), (" 세워요", W_)]),
    ([("그래서 옛날 콜라병은", W_)], [("받침", Y_), ("을 따로 붙였어요", W_)]),
    ([("지금 냉장고 속 콜라병", W_)], [("바닥", Y_), (" 한번 보세요!", W_)]),
    ([("팔로우", Y_), ("하면", W_)], [("매일 하나씩 알려 드릴게요", W_)]),
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
    s = NB
    # 0: 첫 문장 + 큰 5
    if t < s[1]:
        kinetic(im, t, 0.0, s[1], [[[("콜라병", WHITE)], [("바닥은", WHITE)]], [[("왜", WHITE)], [("꽃 모양?", YEL)]]], (1388, 1500), 92, stagger=0.14, slam=0.6)
        k = ease(t / 0.18); a_out = 1 - ease((t - (s[1] - 0.2)) / 0.2)
        put(im, line_img((("?", YEL),), 260), 860, 1110, k * a_out, (1 + 0.15 * (1 - ease(t / 0.25))) * (1 + 0.03 * math.sin(t * 9)))
    if s[1] <= t < s[2]:
        pop(im, t, s[1] + 0.2, box_img("생수병 = 평평", 52, WHITE, INK, pad=34), 300, 520)
        pop(im, t, s[1] + 1.1, box_img("탄산 = 꽃 모양", 52, YEL, INK, pad=34), 780, 620)
    if s[2] <= t < s[3]:
        pop(im, t, s[2] + 0.9, box_img("불룩!", 70, RED, WHITE, pad=40), 800, 260)
    if s[4] <= t < s[5]:
        pop(im, t, s[4] + 0.3, box_img("다리 5개 = 힘 분산", 60, YEL, INK, pad=38), 540, 280)
    if t >= s[7]:
        put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, 1252, 1.0, 0.6 + 0.4 * back((t - s[7]) / 0.28))
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
    thud(0.05, .45); popf(0.9, 900, .22)
    for i in range(1, len(s) - 1):
        whoosh(s[i]); popf(s[i] + 0.05, 820, .16)
    popf(s[1] + 0.2); popf(s[1] + 1.1, 950); popf(s[2] + 0.9, 600, .24)
    thud(s[3] + 2.36, .4); ding(s[3] + 2.4, 990)                     # 압력계 5~7기압
    popf(s[4] + 0.3, 900); thud(s[5] + 2.85, .45); ding(s[5] + 2.9, 1175)  # 받침 '딱!'
    ding(s[7], 1319); ding(s[7] + 0.14, 1760)
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
