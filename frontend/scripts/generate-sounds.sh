#!/bin/bash

# 创建音效目录
mkdir -p ../public/assets/sounds

# 使用 ffmpeg 生成音效
ffmpeg -f lavfi -i "sine=frequency=1000:duration=0.1" ../public/assets/sounds/card.mp3
ffmpeg -f lavfi -i "sine=frequency=800:duration=0.2" ../public/assets/sounds/win.mp3
ffmpeg -f lavfi -i "sine=frequency=400:duration=0.3" ../public/assets/sounds/lose.mp3
ffmpeg -f lavfi -i "sine=frequency=600:duration=0.2" ../public/assets/sounds/level-up.mp3
ffmpeg -f lavfi -i "sine=frequency=200:duration=0.5" ../public/assets/sounds/shuffle.mp3
ffmpeg -f lavfi -i "sine=frequency=500:duration=0.2" ../public/assets/sounds/deal.mp3
ffmpeg -f lavfi -i "sine=frequency=300:duration=0.1" ../public/assets/sounds/button.mp3
ffmpeg -f lavfi -i "sine=frequency=700:duration=0.3" ../public/assets/sounds/firework.mp3 