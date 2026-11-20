#!/bin/bash
# 26편 실사판 합성 v2 (Higgsfield 샌드박스). 클립 c0..c5(1차) + t0..t3(2차: 묶기 3단계, 뒤꿈치 살짝 들림)
# 구간: 0-6.87 c0 | 6.87-10.0 t3(뒤꿈치) | 10.0-12.23 c2 | 12.23-16.23 t0(①고리) | 16.23-18.43 t1(②통과) | 18.43-21.64 t2(③당기고 묶기)
#       21.64-25.19 c3 | 25.19-31.24 c4 뒤쪽 | 31.24-36.45 c5
set -e
cd "$(dirname "$0")"
V="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
seg() { # name src start dur [speed]
  sp=${5:-1}
  ffmpeg -v error -y -ss "$3" -i "$2" -an -vf "setpts=PTS/$sp,$V,tpad=stop_mode=clone:stop_duration=3,trim=duration=$4" -c:v libx264 -crf 16 -preset veryfast -pix_fmt yuv420p "$1.tmp.mp4" && mv "$1.tmp.mp4" "$1.mp4"
}
seg g0 c0.mp4 0.3 6.87
seg g1 t3.mp4 0.2 3.13
seg g2 c2.mp4 0.3 2.23
seg g3 t0.mp4 0 4.00
seg g4 t1.mp4 0.3 2.20 1.5
seg g5 t2.mp4 0.2 3.21 1.15
seg g6 c3.mp4 0.2 3.55
seg g7 c4.mp4 3.6 6.05
seg g8 c5.mp4 0 5.21
printf "file '%s'\n" g0.mp4 g1.mp4 g2.mp4 g3.mp4 g4.mp4 g5.mp4 g6.mp4 g7.mp4 g8.mp4 > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy bg.mp4
ffmpeg -v error -y -i bg.mp4 -c:v libvpx-vp9 -i ov.webm -i audio.m4a \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -t 36.45 -movflags +faststart final.part.mp4
mv final.part.mp4 ep26r.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ep26r.mp4
