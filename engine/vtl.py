"""Narration-driven episode builder shared by ep16+.
LINES: [(spoken, cap1, cap2, scene_fn(r, im, d))]; voice dir vo/<name>h (own recording) else vo/<name>tts."""
import os, sys, json
from kit import *


def rel(fn, t0):
    return lambda t, im, d: fn(t - t0, im, d)


def build(num, name, LINES, T, Q, events, GAP=0.14, qys=(585, 735), qsize=120, spoken=None, emotions=None, breaths=()):
    VO = os.environ.get("VO_DIR") or os.path.join(os.path.dirname(HERE), "work", "vo", name)
    if spoken and not os.path.exists(os.path.join(VO, "meta.json")):
        import natural_vo
        print("generating voice ->", VO, flush=True)
        for r in natural_vo.make(spoken, VO, emotions=emotions, breaths=tuple(breaths), takes=int(os.environ.get("TAKES", 4))):
            print("  line", r, flush=True)
    if not os.path.exists(os.path.join(VO, "meta.json")):
        VO = os.path.join(HERE, "vo", name + "tts")
        os.makedirs(VO, exist_ok=True)
        if not os.path.exists(os.path.join(VO, "meta.json")):
            import tts_st
            durs = [tts_st.say(txt, os.path.join(VO, f"l{i:02d}.wav"), 1.0, 32)[0] for i, (txt, *_r) in enumerate(LINES)]
            json.dump(durs, open(os.path.join(VO, "meta.json"), "w"))
    durs = json.load(open(os.path.join(VO, "meta.json")))
    import soundfile as sf, numpy as np
    spans = []
    for i in range(len(durs)):
        x, sr = sf.read(os.path.join(VO, f"l{i:02d}.wav")); x = x if x.ndim == 1 else x.mean(1)
        idx = np.where(np.abs(x) > 0.02)[0]
        spans.append((idx[0] / sr, idx[-1] / sr) if len(idx) else (0, durs[i]))
    starts, t = [], 0.15
    for (a, e) in spans:
        starts.append(t - a); t = t - a + e + GAP
    starts[1] = max(starts[1], 2.2)
    for i in range(2, len(starts)):
        starts[i] = max(starts[i], starts[i - 1] + spans[i - 1][1] + GAP)
    DUR = round(starts[-1] + spans[-1][1] + 1.0, 2)
    seg = [float(max(0.0, s_ + spans[i][0] - 0.05)) for i, s_ in enumerate(starts)]
    seg[0] = 0.0
    CAPS = [(seg[i], seg[i + 1] if i + 1 < len(seg) else DUR, l1, l2) for i, (_, l1, l2, _s) in enumerate(LINES) if l1]
    SC_ = [(seg[i], rel(fn, seg[i])) for i, (*_x, fn) in enumerate(LINES)]
    EP = Episode(num, T, None, None, SC_, CAPS, events=events(seg), dur=DUR, qhook=(Q, qys, qsize), qend=seg[1], cap_y=(1186, 1290))
    EP.fit = 0.82; EP.end_y = 1100
    EP.CLIPS = [(starts[i], os.path.join(VO, f"l{i:02d}.wav")) for i in range(len(LINES))]
    EP.seg, EP.VO, EP.spoken = seg, VO, spoken
    return EP


def main(EP, tag):
    print("VO", EP.VO, "dur", EP.dur, "seg", [round(x, 2) for x in EP.seg])
    if sys.argv[1] == "frames":
        for tt in sys.argv[2:]:
            EP.frame(float(tt)).save(f"sz/{tag}_{tt}.png")
    elif sys.argv[1] == "render":
        EP.render_voice(sys.argv[2], EP.CLIPS)
