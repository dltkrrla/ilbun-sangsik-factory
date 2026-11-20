#!/bin/bash
# 26편 실사판 합성 (Higgsfield 샌드박스에서 실행). 인자: 클립 URL 6개 (c0..c5)
# 구간(내레이션 시간): 0-6.87 c0 | 6.87-10.0 c1 | 10.0-12.23 c2 | 12.23-21.64 c4 흐림(묶는 법 카드 뒤) | 21.64-25.19 c3 | 25.19-31.24 c4 뒤쪽 | 31.24-36.45 c5
set -e
cd "$(dirname "$0")"
i=0; for u in "$@"; do [ -f c$i.mp4 ] || curl -sfo c$i.mp4 "$u"; i=$((i+1)); done
V="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
seg() { # name src start dur extra
  ffmpeg -v error -y -ss "$3" -i "$2" -t "$4" -an -vf "$V$5,tpad=stop_mode=clone:stop_duration=3,trim=duration=$4" -c:v libx264 -crf 16 -preset veryfast -pix_fmt yuv420p "$1.tmp.mp4" && mv "$1.tmp.mp4" "$1.mp4"
}
seg g0 c0.mp4 0.3 6.87 ""
seg g1 c1.mp4 0.4 3.13 ""
seg g2 c2.mp4 0.3 2.23 ""
seg g3 c4.mp4 0 9.41 ",gblur=sigma=22,eq=brightness=-0.06"
seg g4 c3.mp4 0.2 3.55 ""
seg g5 c4.mp4 3.6 6.05 ""
seg g6 c5.mp4 0 5.21 ""
printf "file '%s'\n" g0.mp4 g1.mp4 g2.mp4 g3.mp4 g4.mp4 g5.mp4 g6.mp4 > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy bg.mp4
ffmpeg -v error -y -i bg.mp4 -c:v libvpx-vp9 -i ov.webm -i audio.m4a \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -t 36.45 -movflags +faststart final.part.mp4
mv final.part.mp4 ep26r.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ep26r.mp4
