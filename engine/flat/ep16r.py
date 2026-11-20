"""16편 리메이크(맥주병은 왜 갈색): 아저씨 연기 클립 + 설계도 모션그래픽 위 투명 오버레이 + 소리.
사실: Cook's Illustrated(10억분의 1g/12온스, 투명 잔 햇빛 창가 30분 → 이취), Science News(갈색 유리 500nm 아래 차단), ASBC(3-MBT 역치 수 ng/L).
usage: python3 ep16r.py audio out.wav | overlay out.webm | stills name t1 t2 ..."""
import os, sys, json, math, subprocess, wave
os.environ.setdefault("SIG", "B")
import numpy as np
from PIL import Image, ImageDraw
import sangsik2 as b
from sangsik2 import *

VO = "/home/claude/work/vo16r2"   # 0번 줄만 힘 있게 다시 읽음(길이는 기존 박자 유지)
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
Q_HIT = [0.12, 0.78, 1.41]   # 말하는 박자에 맞춘 단어별 '쾅'


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
    # 단어가 '팡' 하고 나올 때: 충격파 고리 + 사방으로 튀는 불꽃 + 반짝이 (글자 아래층)
    pos = []
    for words, cy in zip(Q_ROWS, ys):
        ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) * scl for w in words]
        sp = size * 0.26 * scl; x = 540 - (sum(ws) + sp * (len(ws) - 1)) / 2
        for ww in ws:
            pos.append((x + ww / 2, cy, ww)); x += ww + sp
    fx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(fx)
    for k_, (px, py, ww) in enumerate(pos):
        lt = t - Q_HIT[k_]
        if not (0 <= lt < 0.45): continue
        big = 1.35 if k_ == len(pos) - 1 else 1.0
        col = YEL if k_ == len(pos) - 1 else (255, 255, 255)
        p = 1 - (1 - min(1.0, lt / 0.4)) ** 3; fa = (1 - lt / 0.45) * a_out
        rx, ry = (ww / 2 + 30 + 120 * p) * big, (70 + 90 * p) * big           # 충격파 고리(글자 모양 따라 납작한 타원)
        if lt < 0.14:                                                          # 터지는 순간 번쩍
            fl = 1 - lt / 0.14; fr = (ww / 2 + 50) * (0.7 + 0.5 * p) * big
            d.ellipse((px - fr, py - fr * 0.55, px + fr, py + fr * 0.55), fill=col + (int(150 * fl * a_out),))
        d.ellipse((px - rx, py - ry, px + rx, py + ry), outline=col + (int(240 * fa),), width=max(3, int(18 * (1 - p))))
        rng_ = np.random.default_rng(k_ * 7 + 1)
        for j in range(14):                                                   # 불꽃 줄기
            ang = j * 2 * math.pi / 14 + rng_.uniform(-0.15, 0.15)
            r0 = (ww / 2 * abs(math.cos(ang)) + 60 * abs(math.sin(ang))) + 20 + 150 * p * big
            ln = (95 + 55 * rng_.uniform()) * (1 - p * 0.8) * big
            c2 = YEL if j % 2 else (255, 255, 255)
            d.line((px + r0 * math.cos(ang), py + r0 * math.sin(ang) * 0.8, px + (r0 + ln) * math.cos(ang), py + (r0 + ln) * math.sin(ang) * 0.8),
                   fill=c2 + (int(255 * fa),), width=11)
        for j in range(9):                                                    # 반짝이 별
            ang = rng_.uniform(0, 6.28); rr = (ww / 2 + 40 + 190 * p) * big; sx, sy = px + rr * math.cos(ang), py + rr * math.sin(ang) * 0.7
            s_ = 30 * (1 - p * 0.7) * big
            d.polygon([(sx, sy - s_), (sx + s_ * .3, sy - s_ * .3), (sx + s_, sy), (sx + s_ * .3, sy + s_ * .3), (sx, sy + s_), (sx - s_ * .3, sy + s_ * .3), (sx - s_, sy), (sx - s_ * .3, sy - s_ * .3)],
                      fill=YEL + (int(255 * fa),))
    if fx.getbbox():
        from PIL import ImageFilter as _IF
        im.alpha_composite(fx.filter(_IF.GaussianBlur(9))); im.alpha_composite(fx)
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
                    k = ease((t - 1.55) / 0.2)                     # '갈색' 밑줄 쓱
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
    def boom(at, vol=.55):                                # 시작 '둥' (깊은 저음 + 짧은 바람)
        m = int(1.1 * sr); tt = np.arange(m) / sr
        sub = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-tt * 9)) / sr) * env(m, .35)
        nz = rng.standard_normal(m); lp = np.zeros(m); a_ = 0.0
        for i in range(m): a_ += .05 * (nz[i] - a_); lp[i] = a_
        add(at, vol * (sub + 2.5 * lp * env(m, .12)))
    def riser(at, ln, vol=.22, f0=160, f1=900):         # 줌인 동안 점점 차오르는 소리
        m = int(ln * sr); tt = np.arange(m) / sr; k = tt / ln
        f = f0 * (f1 / f0) ** (k ** 1.5); tone = np.sin(2 * np.pi * np.cumsum(f) / sr) + .5 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / sr)
        nz = rng.standard_normal(m); y = np.zeros(m); s_ = 0.0; c_ = .01 + .4 * k ** 2
        for i in range(m): s_ += c_[i] * (nz[i] - s_); y[i] = s_
        amp = k ** 2.2 * (1 - np.clip((k - .97) / .03, 0, 1))
        add(at, vol * amp * (.35 * tone + 2.2 * y))
    def shing(at, vol=.14):                              # 반짝 '팅'
        m = int(.9 * sr); tt = np.arange(m) / sr
        add(at, vol * (np.sin(2 * np.pi * 2637 * tt) + .6 * np.sin(2 * np.pi * 3951 * tt) + .3 * np.sin(2 * np.pi * 5274 * tt)) * env(m, .18))
    def click(at, vol=.12):
        m = int(.03 * sr); add(at, vol * rng.standard_normal(m) * env(m, .004))
    s = NB
    boom(0.0, .6)                                         # 첫 화면 '둥'
    riser(0.1, 1.26, .2)                                  # 맥주병으로 줌인되는 동안 차오름
    shing(Q_HIT[2] + 0.02, .13)                           # '갈색'에서 반짝
    def pang(at, vol=.5, f=520):                         # '팡': 짧은 저음 + 터지는 소리 + 높은 팝
        m = int(.35 * sr); tt = np.arange(m) / sr
        kick = np.sin(2 * np.pi * np.cumsum(60 + 170 * np.exp(-tt * 35)) / sr) * env(m, .07)
        nz = rng.standard_normal(m); hp = np.diff(np.concatenate([[0], nz])) * env(m, .025)
        pop = np.sin(2 * np.pi * np.cumsum(f + 900 * np.exp(-tt * 50)) / sr) * env(m, .04)
        add(at, vol * (kick + .45 * hp + .5 * pop))
    for k_, th in enumerate(Q_HIT):
        pang(th, .55 if k_ < 2 else .7, (440, 560, 700)[k_])
    whoosh(Q_HOLD + 0.2, .3, .12)
    for i in range(1, len(s) - 1):
        whoosh(s[i]); popf(s[i] + 0.05, 820, .16)
    popf(s[1] + 0.91, 1000, .2)                          # 자외선·파란 빛
    thud(s[2] + 1.57, .3); popf(s[2] + 1.86, 900, .18)   # 쪼개짐
    for i_ in range(11): click(s[4] + (0.3 + 0.075 * i_ + 0.22) / 1.024, .06)   # 숫자 굴러가다 멈춤
    riser(s[4] + 0.75 / 1.024, 1.3, .13, 220, 1200)      # 병 속으로 파고드는 줌
    thud(s[4] + 2.12 / 1.024, .3)
    click(s[4] + 2.42 / 1.024, .22); popf(s[4] + 2.45 / 1.024, 1200, .12)    # 조준 '찰칵'
    ding(s[4] + 2.77 / 1.024, 1320)                      # 10억분의 1g
    ding(s[5] + 2.55, 990)                               # 30분
    thud(s[6] + 1.13, .4); popf(s[6] + 1.57, 900, .18)   # 막았다
    ding(s[8], 1319); ding(s[8] + 0.14, 1760)
    x *= 0.55
    for i in range(len(VOD)):
        v, vsr = sf.read(f"{VO}/l{i:02d}.wav")
        if v.ndim > 1: v = v.mean(1)
        if vsr != sr: v = np.interp(np.arange(int(len(v) * sr / vsr)) * vsr / sr, np.arange(len(v)), v)
        st = int((s[i] + 0.12) * sr); v = v[: max(0, n - st)]; x[st:st + len(v)] += (1.3 if i == 0 else 0.95) * v / max(1e-6, np.abs(v).max())
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
