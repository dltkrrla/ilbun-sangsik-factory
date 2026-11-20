#!/bin/bash
# 26편 실사판 v4: 달리기 다시 뽑음(r1), "힐락" 줄 공백 제거로 35.38초
# 0-6.87 s0 다가가기 | 6.87-10.0 t3 걷기 | 10.0-12.23 s2 물집 사진 | 12.23-21.64 u1,u2,u3 직접 촬영
# 21.64-25.19 c3 앞부분 0~2.5초 느리게 | 25.19-31.24 c4 뒤쪽 | 31.24-36.45 s0 멀어지기
set -e
cd "$(dirname "$0")"
V="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30"
enc="-c:v libx264 -crf 16 -preset veryfast -pix_fmt yuv420p"
kb() { # name img frames z0 z1 fx fy
  ffmpeg -v error -y -loop 1 -i "$2" -vf "scale=2256:4032:flags=lanczos,zoompan=z='$4+($5-$4)*(1-cos(PI*on/$3))/2':x='(iw-iw/zoom)*$6':y='(ih-ih/zoom)*$7':d=1:s=1080x1920:fps=30,setsar=1" -frames:v $3 $enc "$1.tmp.mp4" && mv "$1.tmp.mp4" "$1.mp4"
}
seg() { # name src start dur [speed]
  sp=${5:-1}
  ffmpeg -v error -y -ss "$3" -i "$2" -an -vf "setpts=PTS/$sp,$V,tpad=stop_mode=clone:stop_duration=3,trim=duration=$4" $enc "$1.tmp.mp4" && mv "$1.tmp.mp4" "$1.mp4"
}
kb h0 img/s0.png 206 1.0 1.32 0.61 0.36
seg h1 t3.mp4 0.2 3.13
kb h2 img/s2.png 67 1.0 1.12 0.45 0.6
seg h3 u1.mp4 0 4.00
seg h4 u2.mp4 0 2.70
seg h5 u3.mp4 0 2.71
seg h6 r1.mp4 1.3 3.55
seg h7 c4.mp4 3.6 4.98
kb h8 img/s0.png 156 1.25 1.0 0.61 0.36
printf "file '%s'\n" h0.mp4 h1.mp4 h2.mp4 h3.mp4 h4.mp4 h5.mp4 h6.mp4 h7.mp4 h8.mp4 > list4.txt
ffmpeg -v error -y -f concat -safe 0 -i list4.txt -c copy bg4.mp4
ffmpeg -v error -y -i bg4.mp4 -c:v libvpx-vp9 -i ov.webm -i audio.m4a \
  -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" -map "[v]" -map 2:a \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p -c:a aac -b:a 192k -t 35.38 -movflags +faststart f4.part.mp4
mv f4.part.mp4 ep26r4.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 ep26r4.mp4
