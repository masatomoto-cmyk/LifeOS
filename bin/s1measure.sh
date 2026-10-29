#!/bin/bash
# 使い方: measure.sh 名前  … S-1 で C2 を鳴らしながら3秒録音し、音量を測る
D="${S1_MEASURE_DIR:-/tmp/s1measure}"; mkdir -p "$D"
W="$D/$1.wav"
rm -f "$W"
ffmpeg -loglevel error -f avfoundation -i ":1" -t 3 -ac 1 "$W" &
P=$!
sleep 0.4
~/.local/bin/s1 play --dur 2.3 "C2" >/dev/null 2>&1
wait $P
~/.local/bin/s1 panic >/dev/null 2>&1
rms() { ffmpeg -hide_banner -i "$W" -af "$1astats=measure_overall=RMS_level:measure_perchannel=none" -f null - 2>&1 | awk '/RMS level/{print $NF}' | tail -1; }
echo "$1: 全体 $(rms '') dB / 2kHz以上 $(rms 'highpass=f=2000,') dB / 200Hz以下 $(rms 'lowpass=f=200,') dB"
