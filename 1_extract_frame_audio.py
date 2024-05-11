from concurrent.futures import ProcessPoolExecutor
import time
import os
import ffmpeg

def extract_frame_and_audio(video_path, frame_time, duration, frame_output_path, audio_output_path):
    try:
        # 提取视频帧并保存为图片
        (
            ffmpeg
                .input(video_path, ss=frame_time)
                .output(frame_output_path, vf='scale=512:512', vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
        )
        # 提取音频片段并保存为WAV文件
        (
            ffmpeg
                .input(video_path, ss=frame_time)
                .output(audio_output_path, ar='44100', acodec='pcm_s16le', t=duration)
                .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(f"An error occurred while processing time {frame_time}: {e.stderr.decode()}")


def process_video(video_file_data):
    frames_folder, audio_folder, video_file_path, video_file, n = video_file_data
    video_path = os.path.join(video_file_path, video_file)
    try:
        # 获取视频信息
        probe = ffmpeg.probe(video_path)
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        duration = float(video_stream['duration'])
        fps = eval(video_stream['avg_frame_rate'])
        # print('fps: ', fps)
        # 计算视频的总帧数
        total_frames = int(duration * fps)
        
        # 计算每帧的持续时间
        frame_duration = 1 / fps

        for frame_number in range(total_frames):  # 改为从0开始
            frame_time = frame_number / fps
            frame_output_path = os.path.join(frames_folder, f"{n}_{frame_number}.jpg")
            audio_output_path = os.path.join(audio_folder, f"{n}_{frame_number}.wav")
            
            extract_frame_and_audio(video_path, frame_time, frame_duration, frame_output_path, audio_output_path)

    except ffmpeg.Error as e:
        print(f"An error occurred while processing video {video_file}: {e.stderr.decode()}")


def main():
    start_time = time.time()
    video_file_path = '/workspace/dataset/HDTF/difftalk/db_25fps'
    video_files = os.listdir(video_file_path)

    frames_folder = 'data/HDTF/images'
    os.makedirs(frames_folder, exist_ok=True)

    audio_folder = 'data/HDTF/audio_wav'
    os.makedirs(audio_folder, exist_ok=True)

    video_data_list = [
        (frames_folder, audio_folder, video_file_path, video_file, n)
        for n, video_file in enumerate(video_files)
    ]
    
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(process_video, video_data_list)

    end_time = time.time()
    print('Total time taken: {:.2f} seconds'.format(end_time - start_time))

if __name__ == '__main__':
    main()



# # '''
# # 1. Using multiprocessing to speed up processing speed
# # 2. Preserved original audio, preprocessing methods include: converting stereo to mono and normalize
# # 3. keep same length of the video and audio
# # '''

# from moviepy.editor import VideoFileClip
# from multiprocessing import Pool
# import numpy as np
# import os
# from PIL import Image
# import time
# import cv2 
# import ipdb
# import soundfile as sf


# def process_video(video_file_data):
#     frames_folder, audio_folder, video_file_path, video_file, n = video_file_data

#     video_path = os.path.join(video_file_path, video_file)
#     if not video_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
#         return

#     try:
#         video = VideoFileClip(video_path)
#         if video.audio is None:
#             print(f"Video '{video_file}' does not contain audio.")
#             return

#         # 预先读取整个音频数据
#         full_audio_data = video.audio.to_soundarray(fps=44100, nbytes=2)
#         audio_fps = 44100  # 假设音频采样率为44100
#         frame_duration = 1 / video.fps  # 每帧的持续时间
#         expected_length = int(audio_fps * frame_duration)  # 每帧对应的音频采样数

#         for m, frame in enumerate(video.iter_frames(), start=0):
#             if (m * frame_duration) >= video.audio.duration:
#                 break

#             frame_image = Image.fromarray(frame).resize((512, 512), Image.LANCZOS)
#             frame_image.save(os.path.join(frames_folder, f"{n}_{m}.jpg"))

#             start_sample = int(m * frame_duration * audio_fps)
#             end_sample = int((m + 1) * frame_duration * audio_fps)
#             audio_data = full_audio_data[start_sample:end_sample]

#             if len(audio_data) < expected_length:
#                 # 使用 np.pad 来填充音频数据到期望长度
#                 audio_data = np.pad(audio_data, ((0, expected_length - len(audio_data)), (0, 0)), mode='edge')

#             # 保存音频到wav文件
#             sf.write(os.path.join(audio_folder, f"{n}_{m}.wav"), audio_data, audio_fps)

#         video.close()
#     except Exception as e:
#         print(f"An error occurred while processing video {video_file}: {e}")

# def main():
#     start_time = time.time()
#     video_file_path = '/workspace/dataset/HDTF/difftalk/db_25fps'
#     video_files = os.listdir(video_file_path)

#     frames_folder = './data/HDTF/images'
#     os.makedirs(frames_folder, exist_ok=True)

#     audio_folder = './data/HDTF/audio_wav'
#     os.makedirs(audio_folder, exist_ok=True)

#     video_data_list = [(frames_folder, audio_folder, video_file_path, video_file, n) 
#                        for n, video_file in enumerate(video_files, 0)]
#     # 使用全部可用的处理器
#     with Pool(processes=os.cpu_count()) as pool:
#         pool.map(process_video, video_data_list)

#     end_time = time.time()  # 结束计时
#     print('Total time taken: {:.2f} seconds'.format(end_time - start_time))

# '''
# audio数据维度不一致，需要后处理
# ''' 
# if __name__ == '__main__':
#     main()

# '''
# window size:16 
# '''
# from moviepy.editor import VideoFileClip
# import numpy as np
# from PIL import Image
# import os
# from multiprocessing import Pool
# import soundfile as sf
# import ipdb
# import json

# # Helper function to save the audio segment as a wav file
# def save_audio_segment(audio_segment, audio_file_name, sr):
#     try:
#         audio_data = audio_segment.to_soundarray(fps=sr, nbytes=2)
#         if audio_data.size > 0:  # Check if the audio data is not empty
#             sf.write(audio_file_name, audio_data, sr)
#         else:
#             print(f"Audio segment is empty for file {audio_file_name}.")
#     except ValueError as e:
#         print(f"Failed to save audio segment for file {audio_file_name}: {e}")

# # Helper function to extract audio window
# def extract_audio_window(audio, center_time, window_size, video_duration):
#     half_window_size = window_size / 2
#     start_time = max(0, center_time - half_window_size)
#     end_time = min(video_duration, start_time + window_size)
    
#     if end_time > video_duration:
#         # Shift the start_time backward if we're at the end of the video
#         start_time = max(0, video_duration - window_size)
#         end_time = video_duration
#     audio_segment = audio.subclip(start_time, end_time)
    
#     return audio_segment

# # Video processing function
# def process_video(video_file_data):
#     frames_folder, audio_folder, video_file_path, video_file, video_index = video_file_data
#     video_path = os.path.join(video_file_path, video_file)
#     if not video_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
#         return
    
#     try:
#         video = VideoFileClip(video_path)
#         if video.audio is None:
#             print(f"Video '{video_file}' does not contain audio.")
#             return

#         audio = video.audio
#         sr = 22000  # Audio sampling rate in Hz is set to 22kHz
#         fps = 25  # Video frame rate is 25fps
#         video_duration = video.duration  # Get the video duration
#         audio_window_duration = 0.32  # Audio window duration is 320ms

#         for frame_number, frame in enumerate(video.iter_frames(), start=0):
#             frame_file_name = f"{frames_folder}/{video_index}_{frame_number}.jpg"
#             Image.fromarray(frame).save(frame_file_name)
            
#             # Calculate the center time for the audio window corresponding to this frame
#             center_time = (frame_number - 0.5) / fps
#             audio_segment = extract_audio_window(audio, center_time, audio_window_duration, video_duration)
            
#             # Check if audio_segment has non-zero duration
#             if audio_segment.duration > 0:
#                 audio_file_name = f"{audio_folder}/{video_index}_{frame_number}.wav"
#                 save_audio_segment(audio_segment, audio_file_name, sr)
#             else:
#                 print(f"No audio to extract at frame {frame_number} in video {video_file}.")

#         video.close()
#     except Exception as e:
#         print(f"An error occurred while processing video {video_file}: {e}")

# # Main execution function
# def main():
#     video_file_path = '/workspace/dataset/HDTF/difftalk/db_25fps'
#     video_files = os.listdir(video_file_path)

#     frames_folder = './data/HDTF/images'
#     os.makedirs(frames_folder, exist_ok=True)

#     audio_folder = './data/HDTF/audio_wav'
#     os.makedirs(audio_folder, exist_ok=True)

#     video_data_list = [(frames_folder, audio_folder, video_file_path, video_file, n)
#                        for n, video_file in enumerate(sorted(video_files), start=0)]
    
#     with open('./data/HDTF/video_id_map.txt', 'w') as fout:
#         json.dump(video_data_list, fout)
        
#     with Pool(processes=os.cpu_count()) as pool:
#         pool.map(process_video, video_data_list)

# if __name__ == '__main__':
#     main()

