"""Build one episode end to end.
usage: python3 engine/make.py episodes/epNN.py out/epNN.mp4
 1. voice (natural_vo: best of N takes, emotions, mastering) — cached in work/vo/<name>
 2. ASR check of every line (prints a similarity score; < 0.8 means re-generate that line)
 3. render (kit.render_voice)"""
import sys, os, importlib.util, difflib, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
os.chdir(ROOT)
ep_path, out = sys.argv[1], sys.argv[2]
sys.argv = [sys.argv[0], "noop"]
spec = importlib.util.spec_from_file_location("episode", ep_path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
EP = m.EP
import soundfile as sf, natural_vo as nv
norm = lambda t: re.sub(r"[^가-힣a-zA-Z0-9]", "", t)
bad = []
for i, txt in enumerate(EP.spoken or []):
    x, sr = sf.read(os.path.join(EP.VO, f"l{i:02d}.wav")); x = x if x.ndim == 1 else x.mean(1)
    heard = nv.asr(x, sr); r = difflib.SequenceMatcher(None, norm(heard), norm(txt)).ratio()
    print(f"ASR {i}: {r:.2f}  {heard}")
    if r < 0.8: bad.append(i)
print("ASR_LOW_LINES", bad)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
EP.render_voice(os.path.abspath(out), EP.CLIPS)
print("DURATION", EP.dur, "OUT", os.path.abspath(out))
