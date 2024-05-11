import numpy as np
import os
import pandas as pd
import random
import ipdb

dir_path = 'data/HDTF/audio_smooth'

# 过滤并获取文件名列表
files_list = [file.split('.')[0] for file in os.listdir(dir_path) if file.endswith('.npy')]

# 创建DataFrame对象
df = pd.DataFrame({'image_names': files_list})

# 分割字符串获取类别，并转换为整数类型
df['category'] = df['image_names'].str.split('_', expand=True)[0].astype(int)

# 对每个类别进行排序
group = df.groupby('category')['image_names'].apply(lambda lst: sorted(lst, key=lambda x: int(x.split('_')[1])))

# 计算类别总数
dataset_size = len(group.keys())

# 计算训练集大小（55%的数据）
sample_size = int(dataset_size * 0.55)
dataset_keys = list(group.keys())

# 使用随机状态可以确保结果的可复现性
random_state = 42
random.seed(random_state)

# 随机抽取55%的数据作为训练集
train_set = random.sample(dataset_keys, sample_size)

# 使用集合操作来找到测试集的类别键
test_set = set(dataset_keys) - set(train_set)
# ipdb.set_trace()
# 将训练集写入文件, 这里只选择长度大于60的样本作为训练集
with open('data/HDTF/data_train.txt', 'w') as f_train:
    for key in train_set:
        f_train.writelines(f"{file_name}\n" for file_name in group[key] if len(group[key]) > 60)

# 将测试集写入文件, 这里只选择长度大于60的样本作为测试集
with open('data/HDTF/data_test.txt', 'w') as f_test:
    for key in test_set:
        f_test.writelines(f"{file_name}\n" for file_name in group[key] if len(group[key]) > 60)

print(dataset_size)
