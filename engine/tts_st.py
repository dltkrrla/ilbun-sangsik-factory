import os, sherpa_onnx as s, soundfile as sf, sys, json
M = os.environ.get("SANGSIK_MODELS", "/home/claude/models") + "/tts/"
cfg = s.OfflineTtsConfig(model=s.OfflineTtsModelConfig(supertonic=s.OfflineTtsSupertonicModelConfig(
    duration_predictor=M + "duration_predictor.onnx", text_encoder=M + "text_encoder.onnx", vector_estimator=M + "vector_estimator.onnx",
    vocoder=M + "vocoder.onnx", tts_json=M + "tts.json", unicode_indexer=M + "unicode_indexer.bin", voice_style=M + "voice.bin"), num_threads=2))
tts = s.OfflineTts(cfg)


def say(text, out, speed=1.0, steps=8, sid=0):
    g = s.GenerationConfig(); g.speed = speed; g.num_steps = steps; g.sid = sid
    try:
        g.extra = {"lang": "ko"}
    except Exception:
        g.extra = json.dumps({"lang": "ko"})
    a = tts.generate(text, g)
    sf.write(out, a.samples, a.sample_rate)
    return len(a.samples) / a.sample_rate, a.sample_rate


if __name__ == "__main__":
    print(say(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 1.0))
