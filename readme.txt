
1) 视频帧率转为25fps: sh preprocess/0_change_fps.sh 
2) 提取每一帧图像（images），及对应的音频（audio_wav）：python3 preprocess/1_extract_frame_audio.py 
3）使用deepspeech从.wav提取特征，保存为npy（audio_ds）：python3 preprocess/audio/deepspeech_features/extract_ds_features.py --input data/HDTF/audio_wav --output data/HDTF/audio_smooth 注意需要修改deepspeech_features.py中的target_sample_rate = 22000，video_fps参照voca应该设置为60，显示维度信息（1, 16, 29）, 提示frame length (550) is greater than FFT size (512), frame will be truncated, 目前没发现对结果有影响。
4) 检测人脸关键点并归一化（landmarks）：python3 preprocess/2_detect_face_lmk.py 
5) audio_ds相邻8帧取平均，例如当前是第10帧，取7，8，9，10，11，12, 13, 14的均值，重新写入第10帧（audio_smooth）. 一般开头和结尾帧值为空，保留使用0填充: python3 preprocess/3_smooth_audio.py 
6) 使用clean_common_files.py，依次执行第1和2个函数

todo:
1)原始视频文件与预处理后的数据对应关系。已完成，video_id_map.txt 
