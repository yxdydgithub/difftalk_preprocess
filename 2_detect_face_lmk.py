import cv2
import dlib
import os
import numpy as np
from multiprocessing import Pool

# 加载人脸检测器
detector = dlib.get_frontal_face_detector()

# 加载关键点检测模型
predictor = dlib.shape_predictor("./preprocess/shape_predictor_68_face_landmarks.dat")

# image dir path
img_dir = "./data/HDTF/images"
imgs_list = os.listdir(img_dir)

# landmark save path
org_lmk_dir = "./data/HDTF/org_landmarks"
os.makedirs(org_lmk_dir, exist_ok=True)

lmk_dir = "./data/HDTF/landmarks"
os.makedirs(lmk_dir, exist_ok=True)
# landmark image save path
lmk_img_dir = './data/HDTF/lmk_img'
os.makedirs(lmk_img_dir, exist_ok=True)

# 定义归一化函数
def normalize(data):
    min_val = np.min(data, axis=0)
    max_val = np.max(data, axis=0)
    # 避免除以零
    if (max_val - min_val).any() == 0:
        return data
    normalized_data = (data - min_val) / (max_val - min_val)
    return normalized_data
    
def process_image(img):
    img_fpath = os.path.join(img_dir, img)
    image = cv2.imread(img_fpath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        landmarks = predictor(gray, face)
        
        # 为每个面部创建一个空列表来存储关键点
        face_lmk = []

        for n in range(68):
            x = landmarks.part(n).x
            y = landmarks.part(n).y
            cv2.circle(image, (x, y), 1, (255, 0, 0), -1)
            # 这里改为向列表添加关键点
            face_lmk.append((x, y))

        # 在循环结束后，将列表转换为NumPy数组
        face_lmk = np.array(face_lmk)
        
        normalized_lmk = normalize(face_lmk)
        
        lmk_filename = img.split('.')[0] + '.lms'
        
        org_lmk_fpath = os.path.join(org_lmk_dir, lmk_filename)
        np.savetxt(org_lmk_fpath, face_lmk, fmt='%.2f')
        
        normalized_lmk_fpath = os.path.join(lmk_dir, lmk_filename)
        np.savetxt(normalized_lmk_fpath, normalized_lmk, fmt='%f')

    lmk_img_fpath = os.path.join(lmk_img_dir, img)  # 设置关键点图像的保存路径
    cv2.imwrite(lmk_img_fpath, image)

def main():
    # 使用所有可用的CPU核心数
    # with Pool(processes=os.cpu_count()) as pool:
    with Pool(processes=12) as pool:
        pool.map(process_image, imgs_list)

if __name__ == '__main__':
    main()
