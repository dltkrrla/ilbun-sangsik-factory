#!/usr/bin/env bash
# One-time setup for a fresh session: python packages + voice/ASR models (from this repo's release "models-v1").
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
MODELS="${SANGSIK_MODELS:-$HOME/models}"
pip install -q --break-system-packages "sherpa-onnx==2.0.1" pyworld==0.3.5 soundfile numpy pillow >/dev/null
command -v ffmpeg >/dev/null || { echo "ffmpeg missing"; exit 1; }
if [ ! -f "$MODELS/tts/vocoder.onnx" ] || [ ! -f "$MODELS/asr/model.int8.onnx" ]; then
  mkdir -p "$MODELS"; cd "$MODELS"
  base="https://github.com/dltkrrla/ilbun-sangsik-factory/releases/download/models-v1"
  if curl -fsSL -o tts.tar.gz "$base/tts.tar.gz" && curl -fsSL -o asr.tar.gz "$base/asr.tar.gz"; then
    tar xzf tts.tar.gz; tar xzf asr.tar.gz; rm -f tts.tar.gz asr.tar.gz
  else
    # 2026-11-18: release models-v1 is gone (404) -> same models from k2-fsa/sherpa-onnx public releases
    # (Supertonic 3 int8: sid 0-4 female, 5-9 male; our narrator = sid 5) + SenseVoice int8
    rm -f tts.tar.gz asr.tar.gz
    k2="https://github.com/k2-fsa/sherpa-onnx/releases/download"
    T=sherpa-onnx-supertonic-3-tts-int8-2026-05-11; A=sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17
    curl -fsSL "$k2/tts-models/$T.tar.bz2" | tar xj
    curl -fsSL "$k2/asr-models/$A.tar.bz2" | tar xj
    mkdir -p tts asr
    for n in duration_predictor text_encoder vector_estimator vocoder; do ln -sf "$MODELS/$T/$n.int8.onnx" "tts/$n.onnx"; done
    for f in tts.json unicode_indexer.bin voice.bin; do ln -sf "$MODELS/$T/$f" "tts/$f"; done
    ln -sf "$MODELS/$A/model.int8.onnx" asr/model.int8.onnx; ln -sf "$MODELS/$A/tokens.txt" asr/tokens.txt
  fi
fi
# 2026-11-19: the models-v1 release ships a corrupted SenseVoice ASR (md5 7cf0eec0…) that mis-hears every Korean line
# (garbage/Chinese output -> ASR scores 0 and take selection is random). Replace it with the official k2-fsa file.
ASR_OK=0e8e550411d3589be9f0af06f1c8fec3
if [ "$(md5sum "$MODELS/asr/model.int8.onnx" | cut -d' ' -f1)" != "$ASR_OK" ]; then
  echo "ASR model corrupted -> fetching official SenseVoice int8"
  A=sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17
  (cd "$MODELS" && curl -fsSL "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/$A.tar.bz2" | tar xj)
  rm -f "$MODELS/asr/model.int8.onnx"; ln -s "$MODELS/$A/model.int8.onnx" "$MODELS/asr/model.int8.onnx"
fi
# engine defaults to /home/claude/models
[ -e /home/claude/models ] || ln -sfn "$MODELS" /home/claude/models
echo "ready: models in $MODELS"
