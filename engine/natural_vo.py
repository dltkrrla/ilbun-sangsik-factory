"""More human-sounding narration from Supertonic.
make(texts, VO, sid=5, takes=5): for each line generate several takes, keep the one that is read correctly (ASR)
and has the liveliest intonation, vary pace slightly per line, add room tone + soft breaths, light mastering.
Writes VO/l00.wav.. and VO/meta.json (same layout the episode builders expect)."""
import os, json, re, subprocess, difflib, numpy as np, soundfile as sf
import tts_st

_asr = None


def asr(x, sr):
    global _asr
    import sherpa_onnx
    if _asr is None:
        _asr = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=os.environ.get("SANGSIK_MODELS", "/home/claude/models")+"/asr/model.int8.onnx", tokens=os.environ.get("SANGSIK_MODELS", "/home/claude/models")+"/asr/tokens.txt", language="ko", use_itn=False, num_threads=2)
    if sr != 16000:
        n = int(len(x) * 16000 / sr); x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x); sr = 16000
    s = _asr.create_stream(); s.accept_waveform(sr, x.astype("float32")); _asr.decode_stream(s); return s.result.text


def norm(t):
    return re.sub(r"[^가-힣a-zA-Z0-9]", "", t)


def f0_track(x, sr):
    fr = int(sr * 0.04); out = []
    for i in range(0, len(x) - fr, fr // 2):
        w = x[i:i + fr]
        if np.sqrt((w ** 2).mean()) < 0.03: continue
        w = w - w.mean(); ac = np.correlate(w, w, "full")[fr - 1:]
        lo, hi = int(sr / 400), int(sr / 70); k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.3 * ac[0]: out.append(sr / k)
    return np.array(out)


def score(x, sr, text):
    m = difflib.SequenceMatcher(None, norm(asr(x, sr)), norm(text)).ratio()
    f = f0_track(x, sr)
    st = np.std(12 * np.log2(f / np.median(f))) if len(f) > 5 else 0
    st = min(st, 3.2)                       # lively, but not wobbly
    return m * 10 + st, m, st


def breath(sr, dur=0.32, level=0.035, rng=None):
    rng = rng or np.random.default_rng(1)
    n = int(sr * dur); w = rng.standard_normal(n)
    # band-limit roughly 400-2500 Hz with simple FFT mask
    W = np.fft.rfft(w); fr = np.fft.rfftfreq(n, 1 / sr); W[(fr < 400) | (fr > 2500)] = 0; w = np.fft.irfft(W, n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.6
    w = w / (np.abs(w).max() + 1e-9) * env * level
    return w


def make(texts, VO, sid=5, takes=5, steps=32, base_speed=1.04, breaths=(), seed=7, emotions=None):
    os.makedirs(VO, exist_ok=True)
    rng = np.random.default_rng(seed); durs = []; report = []
    for i, text in enumerate(texts):
        sp = base_speed * (1 + rng.uniform(-0.03, 0.03))
        emo_p = None
        if emotions:
            import emote
            emo_p = dict(emote.EMO[emotions[i]]); sp *= emo_p["tempo"]; emo_p["tempo"] = 1.0  # pace from the TTS itself, never by stretching
            emo_p["breathy"] *= 0.5
        best = None
        for k in range(takes):
            tmp = os.path.join(VO, f"_t{i:02d}_{k}.wav")
            tts_st.say(text, tmp, sp, steps, sid)
            x, sr = sf.read(tmp); sc = score(x, sr, text)
            if best is None or sc[0] > best[0][0]:
                best = (sc, x, sr)
            os.remove(tmp)
        (sc, m, st), x, sr = best
        report.append((i, round(m, 2), round(st, 2), round(sp, 3)))
        # trim silence, add a soft breath before chosen lines
        if emotions:
            import emote
            x = emote.apply(x, sr, emo_p, seed=i)
        idx = np.where(np.abs(x) > 0.02)[0]; x = x[max(0, idx[0] - int(.04 * sr)): idx[-1] + int(.12 * sr)]
        if i in breaths:
            x = np.concatenate([breath(sr, rng=rng), np.zeros(int(0.06 * sr)), x])
        raw = os.path.join(VO, f"_raw{i:02d}.wav"); sf.write(raw, x, sr)
        out = os.path.join(VO, f"l{i:02d}.wav")
        master(raw, out); os.remove(raw)
        durs.append(sf.info(out).duration)
    json.dump(durs, open(os.path.join(VO, "meta.json"), "w"))
    return report


def master(src, dst):
    """Warm it up, take the synthetic edge off, put it in a small room with a faint noise floor."""
    af = ("highpass=f=70,equalizer=f=170:t=q:w=1:g=1.5,equalizer=f=2800:t=q:w=1.4:g=1.2,equalizer=f=7500:t=q:w=1.5:g=-2.5,"
          "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=1.5,"
          "aecho=0.9:0.5:18|31:0.08|0.05,loudnorm=I=-16:TP=-1.5:LRA=7")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src, "-filter_complex",
                    f"[0]{af},aresample=44100[v];anoisesrc=c=pink:a=0.0012:r=44100[n];[v][n]amix=inputs=2:duration=first:normalize=0",
                    "-ac", "1", "-ar", "44100", dst], check=True)


if __name__ == "__main__":
    import sys
    texts = json.load(open(sys.argv[1])); VO = sys.argv[2]
    br = tuple(int(v) for v in sys.argv[3].split(",")) if len(sys.argv) > 3 and sys.argv[3] else ()
    emos = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    for r in make(texts, VO, breaths=br, emotions=emos, takes=int(os.environ.get("TAKES", 5))): print(r)
