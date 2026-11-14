import os, sherpa_onnx, soundfile as sf, sys, numpy as np
r = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=os.environ.get("SANGSIK_MODELS", "/home/claude/models")+"/asr/model.int8.onnx", tokens=os.environ.get("SANGSIK_MODELS", "/home/claude/models")+"/asr/tokens.txt", language="ko", use_itn=True, num_threads=2)
for f in sys.argv[1:]:
    x, sr = sf.read(f, dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    if sr != 16000:
        import math
        n = int(len(x) * 16000 / sr); x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype("float32"); sr = 16000
    s = r.create_stream(); s.accept_waveform(sr, x); r.decode_stream(s); print(f.split('/')[-1], "→", s.result.text)
