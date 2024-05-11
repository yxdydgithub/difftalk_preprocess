#!/bin/bash

# WAV文件所在的路径
wavPath="data/HDTF/audio_wav"

# 你的无声视频文件
video="logs/inference/2.mp4"

# 输出文件名
output="logs/inference/2_wav.mp4"

# 临时合并音频文件的名称
audioMerged="merged_audio.wav"

# 切换到WAV文件所在的目录
# cd "$wavPath"

# 使用ffmpeg合并所有匹配的WAV文件
# 注意：在这个例子中，我们使用 $wavPath 路径下的所有匹配文件
ffmpeg -f concat -safe 0 -i <(for f in $wavPath/2_*.wav; do echo "file '$PWD/$f'"; done) -c copy "$audioMerged"

# 切换回原始目录（如果需要），并将合并后的音频添加到视频中
# cd - # 如果你在前面改变了工作目录
ffmpeg -i "$video" -i "$audioMerged" -c:v copy -c:a aac -strict experimental "$output"

# 如果不再需要，可以选择删除临时合并的音频文件
# rm "$wavPath/$audioMerged"
