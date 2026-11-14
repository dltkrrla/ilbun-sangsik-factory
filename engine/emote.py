"""Per-line emotion for TTS speech using the WORLD vocoder.
An emotion changes pitch level, pitch range, pitch contour over the line, pace, loudness and voice colour."""
import numpy as np, pyworld as pw

# shift: semitones · rng: pitch-range multiplier · slope: semitones from start to end of line
# tail: semitones added on the last 25% (+ = rising, question) · tempo: >1 faster · gain dB · bright: spectral tilt dB/oct (+ brighter)
# jitter: random pitch wobble in semitones (tension) · breathy: 0..1
EMO = {
    "neutral":   dict(shift=0,    rng=1.15, slope=0,    tail=0,    tempo=1.00, gain=0,  bright=0,    jitter=0,    breathy=0),
    "curious":   dict(shift=1.0,  rng=1.45, slope=0,    tail=2.5,  tempo=0.97, gain=0,  bright=0.5,  jitter=0,    breathy=0),
    "surprised": dict(shift=2.6,  rng=1.75, slope=-1.5, tail=0,    tempo=1.04, gain=2,  bright=1.0,  jitter=0,    breathy=0),
    "excited":   dict(shift=2.0,  rng=1.6,  slope=0,    tail=0.5,  tempo=1.08, gain=2.5, bright=1.2, jitter=0,    breathy=0),
    "amazed":    dict(shift=2.2,  rng=1.8,  slope=-2.0, tail=0,    tempo=0.95, gain=1.5, bright=0.8, jitter=0,    breathy=0),
    "sad":       dict(shift=-1.4, rng=0.8,  slope=-2.0, tail=0,    tempo=0.86, gain=-3, bright=-1.5, jitter=0,    breathy=0.35),
    "angry":     dict(shift=1.2,  rng=1.5,  slope=-1.0, tail=-1.0, tempo=1.10, gain=3.5, bright=2.0, jitter=0.35, breathy=0),
    "disgust":   dict(shift=-0.8, rng=1.3,  slope=-1.5, tail=0,    tempo=0.92, gain=1,  bright=0.5,  jitter=0.25, breathy=0.15),
    "secret":    dict(shift=-1.0, rng=0.85, slope=0,    tail=0,    tempo=0.94, gain=-2, bright=-0.5, jitter=0,    breathy=0.45),
    "bright":    dict(shift=1.4,  rng=1.45, slope=0,    tail=0.8,  tempo=1.03, gain=1,  bright=0.8,  jitter=0,    breathy=0),
    "explain":   dict(shift=0,    rng=1.3,  slope=-0.8, tail=0,    tempo=1.0,  gain=0,  bright=0,    jitter=0,    breathy=0),
}


def apply(x, fs, emo, seed=0):
    p = dict(EMO[emo]) if isinstance(emo, str) else emo
    x = x.astype(np.float64)
    fp = 5.0
    f0, t = pw.harvest(x, fs, f0_floor=60, f0_ceil=500, frame_period=fp)
    sp = pw.cheaptrick(x, f0, t, fs); ap = pw.d4c(x, f0, t, fs)
    n = len(f0); v = f0 > 0
    # remove octave jumps / spikes in the pitch track (main cause of crackle after resynthesis)
    if v.sum() > 10:
        vi = np.where(v)[0]; fv = f0[vi].copy()
        med = np.array([np.median(fv[max(0, k - 7):k + 8]) for k in range(len(fv))])
        bad = (fv > med * 1.35) | (fv < med / 1.35); fv[bad] = med[bad]
        fv = np.convolve(np.pad(fv, 2, mode="edge"), np.ones(5) / 5, "valid")
        f0 = f0.copy(); f0[vi] = fv
        # drop isolated 1-2 frame voiced/unvoiced flips
        for k in range(1, n - 2):
            if v[k] and not v[k - 1] and not v[k + 1]: f0[k] = 0
    if v.sum() > 5:
        lf = np.log2(np.where(v, f0, 1)); m = np.median(lf[v])
        u = np.linspace(0, 1, n)
        semis = p["shift"] + p["slope"] * u + p["tail"] * np.clip((u - 0.75) / 0.25, 0, 1) ** 1.5
        if p["jitter"]:
            rng = np.random.default_rng(seed); j = np.convolve(rng.standard_normal(n), np.ones(12) / 12, "same")
            semis = semis + j / (np.abs(j).max() + 1e-9) * p["jitter"]
        nl = m + (lf - m) * p["rng"] + semis / 12
        f0 = np.where(v, 2 ** nl, 0)
    # spectral tilt (voice colour)
    if p["bright"]:
        fr = np.linspace(1e-3, fs / 2, sp.shape[1]); octs = np.log2(np.maximum(fr, 250) / 1000)
        sp = sp * (10 ** (p["bright"] * octs / 10))[None, :]
    if p["breathy"]:
        ap = np.clip(ap + p["breathy"] * (1 - ap) * 0.6, 0, 1)
    # tempo: resample frame sequence
    if abs(p["tempo"] - 1) > 1e-3:
        m2 = int(round(n / p["tempo"])); idx = np.linspace(0, n - 1, m2)
        lo = np.floor(idx).astype(int); hi = np.minimum(lo + 1, n - 1); w = (idx - lo)[:, None]
        sp = sp[lo] * (1 - w) + sp[hi] * w; ap = ap[lo] * (1 - w) + ap[hi] * w
        f0n = np.where((f0[lo] > 0) & (f0[hi] > 0), f0[lo] * (1 - w[:, 0]) + f0[hi] * w[:, 0], 0)
        f0 = f0n
    y = pw.synthesize(np.ascontiguousarray(f0), np.ascontiguousarray(sp), np.ascontiguousarray(ap), fs, fp)
    y = y / (np.abs(y).max() + 1e-9) * min(0.95, np.abs(x).max() * 10 ** (p["gain"] / 20))
    return y.astype(np.float32)
