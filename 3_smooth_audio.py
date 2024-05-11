import numpy as np
import os
from tqdm import tqdm
import ipdb
import sys
from multiprocessing import Pool


# def get_frame_paths(input_directory, video_number, frame_dict, total_frames, frames_list):
 
#     # ipdb.set_trace()
#     key, frame_number = frame_dict[0], frame_dict[1]
    
#     # 若当前帧小于4，则从第1帧开始取
#     if key < 4: 
#         start_frame = 0
#         end_frame = min(8, total_frames)
#     # 若当前帧靠近最后一帧，则取最后8帧
#     if key > total_frames - 5:
#         end_frame = total_frames
#         start_frame = max(0, total_frames - 8)
#     else:
#         start_frame = key - 3
#         end_frame = key + 5
#     frame_paths = [
#         os.path.join(input_directory, f"{video_number}_{frames_list[i][1]}.npy")
#         for i in range(start_frame, end_frame)
#     ]
#     # ipdb.set_trace()
#     return frame_paths

# def concat_frames(frame_paths):
#     frames_data = [
#         np.load(frame_path) if np.load(frame_path).size != 0 else np.zeros((1, 16, 29))
#         for frame_path in frame_paths
#     ]
#     frames_np = np.concatenate(frames_data, axis=0, dtype=np.float32)
#     return frames_np

# def process_frames(input_directory, output_directory):
#     npy_files = sorted(
#         [f for f in os.listdir(input_directory) if f.endswith('.npy')],
#         key=lambda x: (int(x.split("_")[0]), int(x.split("_")[1].split(".")[0]))
#     )
#     # 确定总的帧数
#     video_number_to_frames = {}
#     for file_name in npy_files:
#         video_number, frame_number = [int(part) for part in file_name.split('.')[0].split('_')]
#         video_number_to_frames.setdefault(video_number, []).append(frame_number)
#     # 对每个视频的帧号进行排序, 并记录每个帧的索引
#     for video_number, frame_numbers in video_number_to_frames.items():
#         video_number_to_frames[video_number] = [(f, frame_number) for f, frame_number in enumerate(sorted(frame_numbers), 0)]

#     # 处理每个文件
#     for vid_files in tqdm(video_number_to_frames.items()):
#         # ipdb.set_trace()
#         video_number, frames_list = vid_files[0], vid_files[1]
#         total_frames = len(frames_list)
#         if total_frames < 8:
#             sys.exit("Error: not enough frames to smooth")
#         for frame_dict in frames_list:
#             frame_paths = get_frame_paths(input_directory, video_number, frame_dict, total_frames, frames_list)
#             concat_data = concat_frames(frame_paths)
#             # ipdb.set_trace()
#             print(concat_data.shape)
#             if concat_data.shape != (8, 16, 29):
#                 sys.exit("Error: concat_data shape is not correct, {}:{}".format(frame_dict, concat_data.shape))
#             np.save(os.path.join(output_directory, f"{video_number}_{frame_dict[1]}.npy"), concat_data)

# # 输入文件夹路径
# input_directory = 'data/HDTF/audio_ds'
# output_directory = 'data/HDTF/audio_smooth'
# os.makedirs(output_directory, exist_ok=True)

# process_frames(input_directory, output_directory)


'''
 多进程版本
'''
# 获取相邻8帧，例如当前帧编号为10，则获取7,8,9,10,11,12,13,14，开头结尾特殊处理
def get_frame_paths(input_directory, video_number, frame_dict, total_frames, frames_list):
    key, frame_number = frame_dict
    if key < 4:
        start_frame = 0
        end_frame = min(8, total_frames)
    elif key > total_frames - 5:
        end_frame = total_frames
        start_frame = max(0, total_frames - 8)
    else:
        start_frame = key - 3
        end_frame = key + 5

    frame_paths = [
        os.path.join(input_directory, f"{video_number}_{frames_list[i][1]}.npy")
        for i in range(start_frame, end_frame)
    ]
    return frame_paths

# 数据为空使用0填充，一般开头结尾帧为0
def concat_frames(frame_paths):
    frames_data = []
    for frame_path in frame_paths:
        frame = np.load(frame_path)
        if frame.shape == (1, 16, 29):
            frames_data.append(frame)
        elif frame.size == 0:
            frames_data.append(np.zeros((1, 16, 29)))
        else:
            raise ValueError(f"Error: frame shape is not correct, {frame_path}:{frame.shape}")        
    frames_np = np.concatenate(frames_data, axis=0)
    return frames_np

def process_frame(args):
    input_directory, output_directory, video_number, frame_dict, total_frames, frames_list = args
    
    frame_paths = get_frame_paths(input_directory, video_number, frame_dict, total_frames, frames_list)
    concat_data = concat_frames(frame_paths)
    if concat_data.shape != (8, 16, 29):
        raise ValueError(f"Error: concat_data shape is not correct, {frame_dict}:{concat_data.shape}")

    output_file_path = os.path.join(output_directory, f"{video_number}_{frame_dict[1]}.npy")
    np.save(output_file_path, concat_data)

def process_frames_multiprocess(input_directory, output_directory, num_processes=4):
    npy_files = sorted(
        [f for f in os.listdir(input_directory) if f.endswith('.npy')],
        key=lambda x: (int(x.split("_")[0]), int(x.split("_")[1].split(".")[0]))
    )
    
    video_number_to_frames = {}
    for file_name in npy_files:
        video_number, frame_number = [int(part) for part in file_name.rsplit('.')[0].split('_')]
        video_number_to_frames.setdefault(video_number, []).append(frame_number)
    
    for video_number, frame_numbers in video_number_to_frames.items():
        video_number_to_frames[video_number] = [(f, frame_number) for f, frame_number in enumerate(sorted(frame_numbers), 0)]
    
    args_list = []
    for video_number, frames_list in video_number_to_frames.items():
        total_frames = len(frames_list)
        if total_frames < 8:
            raise ValueError("Error: not enough frames to smooth")
        for frame_dict in frames_list:
            args_list.append((input_directory, output_directory, video_number, frame_dict, total_frames, frames_list))
    
    with Pool(num_processes) as pool:
        pool.map(process_frame, args_list)

if __name__ == '__main__':
    input_directory = 'data/HDTF/audio_ds'
    output_directory = 'data/HDTF/audio_smooth'
    os.makedirs(output_directory, exist_ok=True)

    num_processes = 10  # 设置想要使用的进程数量
    process_frames_multiprocess(input_directory, output_directory, num_processes)
