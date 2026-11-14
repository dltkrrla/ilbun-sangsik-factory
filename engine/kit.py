"""Shared engine for 1분 상식 episodes: signature, hook, captions, emoji art, sound, render."""
import os, sys, math, subprocess, wave
os.environ.setdefault("SIG", "B")
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sangsik2 as b
from sangsik2 import (W, H, FPS, SC, IY0, IH, BG, BG_ILL, ILL_MASK, SHIFT, WHITE, YEL, BLUE, INK, RED, GREEN, ORANGE,
                      ease, eio, back, mix, cxy, rr, circ, txt, pill, F, signature2, kinetic, line_img, put, box_img)
from sangsik4 import badge, dashed, lerp, rbox

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MUSIC = os.path.join(ROOT, "assets", "music", "theme.wav")
C0 = (1.0, 540, 760)
Y_, W_ = YEL, WHITE
SKIN = (255, 216, 178)

# ───────── emoji ─────────
_EF = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
_ec = {}
def emoji_img(ch):
    if ch not in _ec:
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((80, 80), ch, font=_EF, embedded_color=True, anchor="mm")
        _ec[ch] = im.crop(im.getbbox())
    return _ec[ch]


def emo(im, x, y, size, ch, cam=C0, rot=0.0, a=1.0, flip=False):
    """Draw emoji centred on world (x, y); size = world height."""
    if a <= 0.02 or size <= 2:
        return
    e = emoji_img(ch)
    if flip:
        e = e.transpose(Image.FLIP_LEFT_RIGHT)
    hpx = max(4, int(size * cam[0] * SC)); wpx = max(4, int(e.width * hpx / e.height))
    e = e.resize((wpx, hpx), Image.LANCZOS)
    if rot:
        e = e.rotate(rot, expand=True, resample=Image.BICUBIC)
    if a < 0.995:
        e.putalpha(e.getchannel("A").point(lambda v: int(v * a)))
    X, Y = cxy(cam, x, y)
    im.alpha_composite(e, (int(X - e.width / 2), int(Y - e.height / 2)))


def panel(d, col):
    rr(d, C0, 70, 280, 1010, 1240, 70, fill=col)


def rings(d, cam, x, y, r0, t, col=YEL, spread=40, w=5, rect=None):
    for ph in (0.0, 0.5):
        p = (t * 1.1 + ph) % 1; R = r0 + spread * p; a = int(255 * (1 - p) ** 1.3)
        if rect:
            hw, hh, rad = rect
            rr(d, cam, x - hw - spread * p, y - hh - spread * p, x + hw + spread * p, y + hh + spread * p, rad + spread * p, outline=col + (a,), width=w)
        else:
            circ(d, cam, x, y, R, outline=col + (a,), width=w)


def kpop(t, t0, dur=0.28):
    return back((t - t0) / dur) if t >= t0 else 0.0


def stamp(d, cam, x, y, text, t, t0, col=RED, size=54):
    if t >= t0:
        pill(d, cam, x, y, text, size, col, WHITE, sc=kpop(t, t0, 0.22))


_PM = None
def clip(img):
    global _PM
    if _PM is None:
        _PM = Image.new("L", BG_ILL.size, 0)
        X0, Y0 = cxy(C0, 70, 280); X1, Y1 = cxy(C0, 1010, 1240)
        ImageDraw.Draw(_PM).rounded_rectangle((X0, Y0, X1, Y1), int(70 * SC), fill=255)
    out = BG_ILL.copy(); out.paste(img, (0, 0), _PM); return out


class Episode:
    """scenes: list of (start_time, fn(t, im, d)); caps: list of (t0, t1, line1, line2) from 3.6 s."""
    def __init__(self, num, title, hook1, hook2, scenes, caps, events=(), dur=27.0, end="comment", qhook=None, qend=2.4, cap_y=(1388, 1500)):
        self.num, self.title, self.hook1, self.hook2 = num, title, hook1, hook2
        self.qhook, self.qend, self.cap_y = qhook, qend, cap_y
        self.scenes, self.caps, self.events, self.dur, self.end = scenes, caps, list(events), dur, end

    def scene_at(self, t):
        fn = self.scenes[0][1]; t0 = 0
        for s, f in self.scenes:
            if t >= s:
                fn, t0 = f, s
        return fn

    def draw(self, t):
        im = BG_ILL.convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
        self.scene_at(t)(t, im, d)
        return clip(im)

    def illus(self, t):
        for s, _ in self.scenes[1:]:
            if s <= t < s + 0.26:
                return Image.blend(self.draw(s - 0.001), self.draw(t), eio((t - s) / 0.26))
        return self.draw(t)

    def frame(self, t):
        b.DUR = self.dur; b.EP_TITLE = self.title
        im = BG.copy()
        k = getattr(self, "fit", 1.0)
        if k == 1.0:
            im.paste(self.illus(t).reduce(SC), (0, IY0 + SHIFT), ILL_MASK)
        else:
            nw, nh = round(W * k), round(IH * k)
            il = self.illus(t).resize((nw, nh), Image.LANCZOS)
            self._fm = ILL_MASK.resize((nw, nh), Image.LANCZOS)
            self._fo = ((W - nw) // 2, IY0 + SHIFT)
            im.paste(il, self._fo, self._fm)
        im = im.convert("RGBA")
        signature2(im, max(t, 0.45) if self.qhook else t)
        if self.qhook:
            self.center_q(im, t)
        elif t < 1.52:
            a = min(1, t / 0.08) * (1 - ease((t - 1.36) / 0.14))
            ov = Image.new("RGBA", (W, IH), (8, 12, 28, 255)); ov.putalpha(ILL_MASK.point(lambda v: int(v * 0.52 * a)))
            im.alpha_composite(ov, (0, IY0 + SHIFT))
        if not self.qhook:
            kinetic(im, t, 0.0, 1.5, self.hook1, (690, 850), 128, stagger=0.17, slam=0.9)
            kinetic(im, t, 1.4, 3.6, self.hook2, (1388, 1500), 84, stagger=0.13, slam=0.5)
        if t >= self.dur - 1.8:
            put(im, box_img("구독하면 매일 1분 상식", 50, YEL, INK, pad=38), 540, getattr(self, "end_y", 1252), 1.0, 0.6 + 0.4 * back((t - self.dur + 1.8) / 0.28))
        for t0, t1, l1, l2 in self.caps:
            if t0 <= t < t1:
                a_out = 1 - ease((t - (t1 - 0.12)) / 0.12) if t1 < self.dur else 1
                for i, (segs, cy) in enumerate(((l1, self.cap_y[0]), (l2, self.cap_y[1]))):
                    lt = t - t0 - i * 0.13
                    if lt >= 0 and segs:
                        put(im, line_img(tuple(segs)), 540, cy + (1 - ease(lt / 0.2)) * 26, ease(lt / 0.12) * a_out, 0.86 + 0.14 * back(lt / 0.22))
        return im.convert("RGB")

    def center_q(self, im, t):
        """Topic question, fully readable from frame 0, centred on the picture."""
        if t >= self.qend:
            return
        out = 1 - ease((t - (self.qend - 0.2)) / 0.2)
        if getattr(self, "fit", 1.0) != 1.0:
            ov = Image.new("RGBA", self._fm.size, (8, 12, 28, 255)); ov.putalpha(self._fm.point(lambda v: int(v * 0.42 * out)))
            im.alpha_composite(ov, self._fo)
        else:
            ov = Image.new("RGBA", (W, IH), (8, 12, 28, 255)); ov.putalpha(ILL_MASK.point(lambda v: int(v * 0.42 * out)))
            im.alpha_composite(ov, (0, IY0 + SHIFT))
        rows, ys, size = self.qhook
        tmp = ImageDraw.Draw(Image.new("RGBA", (4, 4))); f = F(size); idx = 0
        for words, cy in zip(rows, ys):
            ws = [sum(tmp.textlength(sg, font=f) for sg, _ in w) for w in words]
            sp = size * 0.34; x = 540 - (sum(ws) + sp * (len(ws) - 1)) / 2
            for w, ww in zip(words, ws):
                lt = t - idx * 0.12; idx += 1
                sc = 1 + 0.1 * (1 - ease(max(0, lt) / 0.22))
                if any(c == YEL for _, c in w):
                    sc *= 1 + 0.05 * math.sin(t * 14)
                put(im, line_img(tuple(w), size), x + ww / 2, cy, out, sc)
                x += ww + sp

    # ───────── sound ─────────
    def sfx(self, path):
        sr = 44100; n = int(self.dur * sr); x = np.zeros(n); rng = np.random.default_rng(self.num)
        def add(at, sig):
            i = int(at * sr)
            if i >= n: return
            if i < 0:
                sig = sig[-i:]; i = 0
            sig = sig[: n - i]; x[i:i + len(sig)] += sig
        def env(m, dd): return np.exp(-np.arange(m) / sr / dd)
        def pop(at, f0=620, vol=.22):
            m = int(.12 * sr); tt = np.arange(m) / sr
            add(at, vol * np.sin(2 * np.pi * (f0 + 380 * np.exp(-tt * 40)) * tt) * env(m, .03))
        def whoosh(at, ln=.38, vol=.2):
            m = int(ln * sr); z = rng.standard_normal(m); y = np.zeros(m); s = 0.0; a = np.linspace(.02, .35, m)
            for i in range(m):
                s += a[i] * (z[i] - s); y[i] = s
            add(at - ln * .6, vol * 3 * y * np.sin(np.pi * np.arange(m) / m) ** 2)
        def ding(at, f=1320, vol=.16, dd=.22):
            m = int(.7 * sr); tt = np.arange(m) / sr
            add(at, vol * (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.01 * tt)) * env(m, dd))
        def thud(at, vol=.45):
            m = int(.25 * sr); tt = np.arange(m) / sr
            add(at, vol * np.sin(2 * np.pi * np.cumsum(50 + 120 * np.exp(-tt * 30)) / sr) * env(m, .07) + .25 * rng.standard_normal(m) * env(m, .006))
        def buzz(at, vol=.2):
            m = int(.28 * sr); tt = np.arange(m) / sr
            add(at, vol * np.sign(np.sin(2 * np.pi * 150 * tt)) * env(m, .12) * .6)
        def clank(at, vol=.2):
            m = int(.5 * sr); tt = np.arange(m) / sr
            add(at, vol * sum(np.sin(2 * np.pi * f * tt) * g for f, g in ((620, 1), (1530, .6), (2710, .4))) * env(m, .09))
        def click(at, vol=.25):
            m = int(.03 * sr); add(at, vol * rng.standard_normal(m) * env(m, .004))
        K = dict(pop=pop, whoosh=whoosh, ding=ding, thud=thud, buzz=buzz, clank=clank, click=click,
                 yes=lambda at: (ding(at, 1047), ding(at + .14, 1568)), no=lambda at: (buzz(at), thud(at, .3)))
        for t0, *_ in self.caps:
            pop(t0 + .02)
        if self.qhook:
            n = sum(len(r) for r in self.qhook[0])
            for i in range(n):
                pop(.02 + .12 * i, 700 + 70 * i, .24)
        else:
            pop(.17, 760, .22); pop(.34, 920, .26)
            for i in range(4):
                pop(1.52 + .13 * i, 700 + 80 * i, .18)
            whoosh(1.5, .3, .16)
        for s, _ in self.scenes[1:]:
            whoosh(s)
        for ev in self.events:
            K[ev[0]](*ev[1:])
        ding(self.dur - 1.8, 1319); ding(self.dur - 1.66, 1760)
        x = np.tanh(x * 1.3) * .9
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype(np.int16).tobytes())

    def render(self, final):
        tag = f"ep{self.num}"; sfxp = os.path.join(HERE, f"{tag}_sfx.wav"); tmp = os.path.join(HERE, f"{tag}.part.mp4")
        self.sfx(sfxp); fo = self.dur - 0.8
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-i", MUSIC, "-i", sfxp,
                              "-filter_complex", f"[1:a]atrim=0:{self.dur},volume=-9dB,afade=t=in:d=0.05,afade=t=out:st={fo}:d=0.8[m];[2:a]volume=0dB[s];[m][s]amix=inputs=2:normalize=0[a]",
                              "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-t", str(self.dur), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for i in range(int(self.dur * FPS)):
            p.stdin.write(self.frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, final); print("ok", final)

    def render_voice(self, final, clips, music_db=-15.0, sfx_db=-4.0):
        """clips: list of (start_time, wav_path). Music and effects are ducked under the voice."""
        import soundfile as sf
        tag = f"ep{self.num}v"; sfxp = os.path.join(HERE, f"{tag}_sfx.wav"); mixp = os.path.join(HERE, f"{tag}_mix.wav"); tmp = os.path.join(HERE, f"{tag}.part.mp4")
        self.sfx(sfxp); sr = 44100; n = int(self.dur * sr)
        def load(p):
            x, r = sf.read(p, dtype="float32")
            x = x.mean(1) if x.ndim > 1 else x
            if r != sr:
                m = int(len(x) * sr / r); x = np.interp(np.linspace(0, len(x) - 1, m), np.arange(len(x)), x).astype("float32")
            return x
        voice = np.zeros(n, np.float32)
        for t0, p in clips:
            v = load(p); i = int(t0 * sr)
            if i < 0:
                v = v[-i:]; i = 0
            v = v[: max(0, n - i)]; voice[i:i + len(v)] += v
        pk = np.abs(voice).max()
        if pk > 0: voice *= 0.89 / pk
        env = np.convolve((np.abs(voice) > 0.02).astype(np.float32), np.ones(int(.25 * sr)) / int(.25 * sr), "same")
        duck = 1 - 0.55 * np.clip(env * 3, 0, 1)
        mus = load(MUSIC)[:n]; mus = np.pad(mus, (0, n - len(mus)))
        t = np.arange(n) / sr; fade = np.clip((self.dur - t) / 0.8, 0, 1)
        fx = load(sfxp)[:n]; fx = np.pad(fx, (0, n - len(fx)))
        mix = voice + mus * 10 ** (music_db / 20) * duck * fade + fx * 10 ** (sfx_db / 20) * (0.6 + 0.4 * duck)
        mix = np.tanh(mix * 1.1) * 0.95
        sf.write(mixp, mix, sr)
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-i", mixp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                              "-c:a", "aac", "-b:a", "192k", "-t", str(self.dur), "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for i in range(int(self.dur * FPS)):
            p.stdin.write(self.frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() != 0:
            raise SystemExit("ffmpeg failed")
        os.replace(tmp, final); print("ok", final)

    def main(self):
        if sys.argv[1] == "stills":
            ims = [self.frame(float(v)).resize((360, 640), Image.LANCZOS) for v in sys.argv[3:]]
            s = Image.new("RGB", (360 * len(ims), 640))
            for i, im in enumerate(ims):
                s.paste(im, (i * 360, 0))
            s.save(os.path.join(HERE, "prev", f"{sys.argv[2]}.jpg"), quality=86)
        else:
            self.render(sys.argv[2])


HOOK_KNOW = [[[("이거", WHITE)]], [[("알고", YEL)], [("있었나요?", YEL)]]]
HOOK_REAL = [[[("이거", WHITE)]], [[("진짜", YEL)], [("일까요?", YEL)]]]
