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
  for f in tts.tar.gz asr.tar.gz; do
    curl -fsSL -o "$f" "$base/$f"
  done
  tar xzf tts.tar.gz
  tar xzf asr.tar.gz
  rm -f tts.tar.gz asr.tar.gz
fi
echo "ready: models in $MODELS"
