"""Make the last syllable sing-song: '알려 주세요~~~'"""
import sys, json, numpy as np, soundfile as sf, pyworld as pw
import tts_st, emote, natural_vo as nv
text, out = sys.argv[1], sys.argv[2]
best=None
for k in range(4):
    tts_st.say(text, "/tmp/_l.wav", 1.02, 32, 5); x, sr = sf.read("/tmp/_l.wav")
    sc = nv.score(x, sr, text)
    if best is None or sc[0] > best[0][0]: best = (sc, x, sr)
(_, x, sr) = best
x = emote.apply(x, sr, "bright").astype(np.float64)
idx = np.where(np.abs(x) > 0.02)[0]; x = x[max(0, idx[0]-int(.04*sr)): idx[-1]+int(.05*sr)]
fp = 5.0
f0, t = pw.harvest(x, sr, f0_floor=60, f0_ceil=500, frame_period=fp)
sp = pw.cheaptrick(x, f0, t, sr); ap = pw.d4c(x, f0, t, sr)
v = np.where(f0 > 0)[0]; end = v[-1]
# last syllable: last voiced run back ~0.22 s
L = int(0.22 * 1000 / fp); s0 = max(0, end - L)
seg = slice(s0, end + 1); n = end + 1 - s0
stretch = 3.4; m = int(n * stretch); idx = np.linspace(0, n - 1, m)
lo = np.floor(idx).astype(int); hi = np.minimum(lo + 1, n - 1); w = (idx - lo)[:, None]
spS = sp[seg][lo] * (1 - w) + sp[seg][hi] * w; apS = ap[seg][lo] * (1 - w) + ap[seg][hi] * w
base = np.median(f0[seg][f0[seg] > 0])
u = np.linspace(0, 1, m)
# rise, then wavy fall:  ~ shape
semis = 3.2 * np.sin(np.pi * np.clip(u / 0.35, 0, 1) / 2) - 5.0 * np.clip((u - 0.35) / 0.65, 0, 1) ** 1.3 + 0.9 * np.sin(u * 2 * np.pi * 2.2) * np.clip((u - 0.3) / 0.7, 0, 1)
f0S = base * 2 ** (semis / 12)
# fade energy at the very end
fade = np.ones(m); k = int(m * 0.3); fade[-k:] = np.linspace(1, 0.25, k) ** 1.5
spS = spS * (fade ** 2)[:, None]
f0n = np.concatenate([f0[:s0], f0S, f0[end + 1:]]); spn = np.vstack([sp[:s0], spS, sp[end + 1:]]); apn = np.vstack([ap[:s0], apS, ap[end + 1:]])
y = pw.synthesize(np.ascontiguousarray(f0n), np.ascontiguousarray(spn), np.ascontiguousarray(apn), sr, fp)
y = y / np.abs(y).max() * 0.9
sf.write("/tmp/_lilt_raw.wav", y, sr); nv.master("/tmp/_lilt_raw.wav", out)
print("dur", sf.info(out).duration)
