import base64, json, os, re, sys
src, out = sys.argv[1], sys.argv[2]
pkgs = {"@3sln/donki-lle-voice-multi": "x1", "@3sln/donki-lle-voice-multi-2": "x2", "@3sln/donki-lle-voice-multi-3": "x3"}
spec = {"duration_predictor.onnx": ["x1/000"], "text_encoder.onnx": ["x1/001", "x1/002", "x1/003", "x1/004"],
        "vector_estimator.onnx": ["x1/005", "x1/006", "x1/007", "x2/000", "x2/001", "x2/002", "x2/003", "x2/004", "x2/005"],
        "vocoder.onnx": ["x2/006", "x2/007", "x3/000"], "tts.json": ["x3/001"], "unicode_indexer.bin": ["x3/002"], "voice.bin": ["x3/003"]}
sizes = {"duration_predictor.onnx": 3700147, "text_encoder.onnx": 36416150, "vector_estimator.onnx": 78400833, "vocoder.onnx": 25991073,
         "tts.json": 8253, "unicode_indexer.bin": 262144, "voice.bin": 517168}
for name, parts in spec.items():
    data = b""
    for p in parts:
        d, n = p.split("/")
        txt = open(os.path.join(src, d, "package", "c", n + ".js"), encoding="ascii").read()
        m = re.fullmatch(r'\s*export default "([A-Za-z0-9+/=]*)";?\s*', txt)
        if not m:
            raise SystemExit("unexpected format in " + p)
        data += base64.b64decode(m.group(1))
    assert len(data) == sizes[name], (name, len(data), sizes[name])
    open(os.path.join(out, name), "wb").write(data)
    print(name, len(data))
