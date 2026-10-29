#!/bin/bash
# S-1 の無音を測る（-inf か約 -90dB 以下なら正常、-60〜-48dB が続けば鳴りっぱなし）
D="${S1_MEASURE_DIR:-/tmp/s1measure}"; mkdir -p "$D"
ffmpeg -loglevel error -f avfoundation -i ":1" -t 1.5 -ac 1 -y "$D/silence.wav" 2>/dev/null
ffmpeg -hide_banner -i "$D/silence.wav" -af astats=measure_overall=RMS_level:measure_perchannel=none -f null - 2>&1 | awk '/RMS level/{print $NF}'
