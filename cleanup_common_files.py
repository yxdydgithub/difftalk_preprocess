import os
from pathlib import Path
import ipdb
import numpy as np
from multiprocessing import Pool, cpu_count
import glob
import re

def cleanup_common_files(folder1_path, folder2_path, folder3_path):
    # 转换为Path对象
    folder1 = Path(folder1_path)
    folder2 = Path(folder2_path)
    folder3 = Path(folder3_path)

    # 获取每个文件夹中的文件名集合
    files1 = {file.stem for file in folder1.iterdir() if file.is_file()}
    files2 = {file.stem for file in folder2.iterdir() if file.is_file()}
    files3 = {file.stem for file in folder3.iterdir() if file.is_file()}
    # ipdb.set_trace()
    # 获取所有文件夹中都存在的文件集合
    common_files = files1 & files2 & files3

    # 定义删除文件的内部函数
    def cleanup_folder(folder, common_file_stems):
        for file in folder.iterdir():
            if file.is_file() and file.stem not in common_file_stems:
                try:
                    os.remove(file)  # 删除文件
                    print(f'Deleted {file}')
                except OSError as e:
                    print(f'Error: {file} : {e.strerror}')

    # 清理三个文件夹
    cleanup_folder(folder1, common_files)
    cleanup_folder(folder2, common_files)
    cleanup_folder(folder3, common_files)

def filter_txt_with_folder_files(folder_path, txt_file_path, output_txt_file_path):
    # 获取文件夹中所有文件的文件名
    folder_files = {file.stem for file in Path(folder_path).iterdir() if file.is_file()}

    # 读取文本文件中的所有行/文件名
    with open(txt_file_path, 'r') as file:
        txt_file_lines = file.readlines()

    # 过滤掉不在文件夹中的文件名
    filtered_lines = [line for line in txt_file_lines if line.strip() in folder_files]

    # 将过滤后的文件名写入新的文本文件
    with open(output_txt_file_path, 'w') as file:
        file.writelines(filtered_lines)

    print(f'Filtered txt file saved to: {output_txt_file_path}')

# create train_name.txt
def save_full_path(input_dir, output_txt):
    files_list = os.listdir(input_dir)
    for file in files_list:
        file_fpath = os.path.join(input_dir, file)
        with open(output_txt, "a") as fout:
            fout.write(file_fpath + '\n')

def check_audio_length(audio_dir):
    audios_list = os.listdir(audio_dir)
    n = 0
    for audio in audios_list:
        audio_fpath = os.path.join(audio_dir, audio)
        if not audio_fpath.lower().endswith('.npy'):
            continue
        audio_data = np.load(audio_fpath)
        print('audio_data_shape: ', audio_data.shape)
        print(audio_data)
        # assert audio_data.shape[0] == 1764, '{} length is not 1764'.format(audio_fpath)
        # if audio_data.shape[0] != 1764:
        #     os.remove(audio_fpath)
        #     print(audio_data.shape[0], ', remove: ', audio_fpath)
        n += 1
    print('Finished! n=', n)
    
def trim_and_save_npy(file_path):
    # 加载.npy文件
    data = np.load(file_path)
    
    # 确保数据至少有1765个元素
    if data.shape[0] > 1764:
        # 裁剪数据到（1764，2）的形状
        trimmed_data = data[:1764, :]
        
        # 保存裁剪后的数据到.npy文件，覆盖原文件
        np.save(file_path, trimmed_data)

def process_files_concurrently(folder_path):
    # 获取文件夹中的所有.npy文件
    file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.npy')]
    
    # 创建一个进程池
    with Pool() as pool:
        # 将文件处理任务分配给进程池
        pool.map(trim_and_save_npy, file_paths)
        
    print(f"Processed {len(file_paths)} files.")

def normalize_data(input_folder_path, output_folder_path):
    """
    读取指定文件夹中的所有.txt文件，进行归一化处理，并保存到另一个文件夹。

    :param input_folder_path: 包含原始.txt文件的文件夹路径
    :param output_folder_path: 存储归一化后.txt文件的文件夹路径
    """
    
    # 确保输出文件夹存在
    os.makedirs(output_folder_path, exist_ok=True)

    # 读取输入文件夹中的所有txt文件
    txt_files = glob.glob(os.path.join(input_folder_path, '*.lms'))

    # 定义归一化函数
    def normalize(data):
        min_val = np.min(data, axis=0)
        max_val = np.max(data, axis=0)
        # 避免除以零
        if (max_val - min_val).any() == 0:
            return data
        normalized_data = (data - min_val) / (max_val - min_val)
        return normalized_data

    # 遍历所有文件
    for file_path in txt_files:
        # 读取文件内容
        with open(file_path, 'r') as file:
            # 使用空白字符进行分割
            data = np.array([list(map(float, re.split('\s+', line.strip()))) for line in file if line.strip()])

        # 归一化数据
        normalized_data = normalize(data)

        # 获取原始文件名
        basename = os.path.basename(file_path)
        
        # 构建输出文件的路径
        output_file_path = os.path.join(output_folder_path, basename)
        
        # 保存归一化后的数据到新的txt文件中
        with open(output_file_path, 'w') as file:
            for item in normalized_data:
                file.write(' '.join(map(str, item)) + '\n')  # 这里也使用空格作为分隔符

    print('All files have been normalized and saved to the output directory.')
    
if __name__ == "__main__":
    # 1. 遍历三个文件夹中的文件，保留同时存在的文件, 不考虑文件名后缀
    # cleanup_common_files('data/HDTF/audio_smooth', 'data/HDTF/images', 'data/HDTF/landmarks')
    # 2. 根据文件夹中的文件名，删除txt中多余的文件名
    # filter_txt_with_folder_files('data/HDTF/images', 'data/org_data_train.txt', 'data/data_train.txt')
    filter_txt_with_folder_files('data/HDTF/images', 'data/org_data_test.txt', 'data/data_test.txt')
    
    # 3. 文件夹中，所有文件的完整路径写入txt
    # save_full_path('/workspace/dataset/HDTF/difftalk/db_25fps', 'data/train_name.txt')
    
    # 4. 废弃，在3_smooth_audio.py中已完成，check audio length
    # check_audio_length('data/HDTF/audio_npy')
    # 5. 废弃，在3_smooth_audio.py中已完成，裁剪音频文件至目标长度
    # process_files_concurrently('./data/HDTF/audio_smooth')
    # 6. 废弃，以合并到2_detect_face_lmk.py
    # normalize_data('data/HDTF/landmarks_org_scale', 'data/HDTF/landmarks')
