#!/bin/bash
# 31편 페트병 바닥 실사판 합성 (Higgsfield 샌드박스). 사물 장면은 AI 사진 + 카메라 이동(모양 안 변함), 기포만 AI 영상(v0).
# 줄 경계: 0 2.58 6.77 11.27 15.64 19.94 24.39 27.67 30.51
set -e
cd "$(dirname "$0")"
V="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
enc="-c:v libx264 -crf 16 -preset veryfast -pix_fmt yuv420p"
kb() { # name img frames z0 z1 fx fy
  ffmpeg -v error -y -loop 1 -i "$2" -vf "scale=2256:4032:flags=lanczos,zoompan=z='$4+($5-$4)*(1-cos(PI*on/$3))/2':x='(iw-iw/zoom)*$6':y='(ih-ih/zoom)*$7':d=1:s=1080x1920:fps=30,setsar=1" -frames:v $3 $enc "$1.tmp.mp4" && mv "$1.tmp.mp4" "$1.mp4"
}
seg() { # name src start dur
  ffmpeg -v error -y -ss "$3" -i "$2" -an -vf "$V,tpad=stop_mode=clone:stop_duration=3,trim=duration=$4" $enc "$1.tmp.mp4" && mv "$1.tmp.mp4" "$1.mp4"
}
kb k0 img/i4.png 77 1.0 1.25 0.5 0.5
kb k1 img/i1.png 126 1.0 1.15 0.5 0.4
seg k2 v0.mp4 0.2 4.50
kb k3 img/i3.png 131 1.0 1.15 0.45 0.75
kb k4 img/i0.png 129 1.0 1.25 0.35 0.6
kb k5 img/i5.png 134 1.0 1.15 0.5 0.75
kb k6 img/i6.png 98 1.0 1.15 0.6 0.4
kb k7 img/i4.png 86 1.25 1.0 0.5 0.5
printf "file '%s'\n" k0.mp4 k1.mp4 k2.mp4 k3.mp4 k4.mp4 k5.mp4 k6.mp4 k7.mp4 > list.txt
ffmpeg -v error -y -f concat -safe 0 -i list.txt -c copy bg.mp4
ffmpeg -v error -y -i bg.mp4 -c:v libvpx-vp9 -i ov.webm -i audio.m4a \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -t 30.5 -movflags +faststart f.part.mp4
mv f.part.mp4 ep31r.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ep31r.mp4
