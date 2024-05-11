# #!/bin/bash

# # 设置源视频文件夹路径
# SOURCE_FOLDER="/workspace/dataset/HDTF/dataset/1_crop_dataset"
# # 设置目标视频文件夹路径
# OUTPUT_FOLDER="/workspace/dataset/HDTF/difftalk/db_25fps"
# # 设置目标帧率（根据需要更改）
# TARGET_FRAMERATE=25

# # 创建输出文件夹，如果它不存在的话
# mkdir -p "$OUTPUT_FOLDER"

# # 遍历文件夹中的所有 mp4 文件
# for FILE in "$SOURCE_FOLDER"/*.mp4; do
#     # 获取没有路径的文件名
#     FILENAME=$(basename "$FILE")
#     # 使用 ffmpeg 更改帧率
#     ffmpeg -i "$FILE" -r "$TARGET_FRAMERATE" "$OUTPUT_FOLDER/$FILENAME"
# done

# echo "Frame rate conversion completed for all videos."

#!/bin/bash

# 设置源视频文件夹路径
SOURCE_FOLDER="/workspace/dataset/HDTF/dataset/1_crop_dataset"
# 设置目标视频文件夹路径
OUTPUT_FOLDER="/workspace/dataset/HDTF/difftalk/db_25fps"
# 设置目标帧率（根据需要更改）
TARGET_FRAMERATE=25

# 创建输出文件夹，如果它不存在的话
mkdir -p "$OUTPUT_FOLDER"

# 导出必要的环境变量
export SOURCE_FOLDER OUTPUT_FOLDER TARGET_FRAMERATE

# 使用 parallel 更改帧率
find "$SOURCE_FOLDER" -name '*.mp4' | parallel ffmpeg -i {} -r "$TARGET_FRAMERATE" "$OUTPUT_FOLDER/{/.}.mp4"

echo "Frame rate conversion completed for all videos."
