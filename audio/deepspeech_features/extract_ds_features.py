"""
    Script for extracting DeepSpeech features from audio file.
"""

import os, ipdb
import argparse
import numpy as np
import pandas as pd
from deepspeech_store import get_deepspeech_model_file
from deepspeech_features import conv_audios_to_deepspeech
from concurrent.futures import ThreadPoolExecutor

def parse_args():
    """
    Create python script parameters.
    Returns
    -------
    ArgumentParser
        Resulted args.
    """
    parser = argparse.ArgumentParser(
        description="Extract DeepSpeech features from audio file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="path to input audio file or directory")
    parser.add_argument(
        "--output",
        type=str,
        help="path to output file with DeepSpeech features")
    parser.add_argument(
        "--deepspeech",
        type=str,
        default='~/.tensorflow/models/deepspeech-0_1_0-b90017e8.pb',
        help="path to DeepSpeech 0.1.0 frozen model")
    parser.add_argument(
        "--metainfo",
        type=str,
        help="path to file with meta-information")

    args = parser.parse_args()
    return args


def extract_features(in_audios, out_files, deepspeech_pb_path, output_dir, metainfo_file_path=None):
    """
    Real extract audio from video file.
    Parameters
    ----------
    in_audios : list of str
        Paths to input audio files.
    out_files : list of str
        Paths to output files with DeepSpeech features.
    deepspeech_pb_path : str
        Path to DeepSpeech 0.1.0 frozen model.
    metainfo_file_path : str, default None
        Path to file with meta-information.
    """
    #deepspeech_pb_path="/disk4/keyu/DeepSpeech/deepspeech-0.9.2-models.pbmm"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    if metainfo_file_path is None:
        num_frames_info = [None] * len(in_audios)
    else:
        train_df = pd.read_csv(
            metainfo_file_path,
            sep="\t",
            index_col=False,
            dtype={"Id": np.int, "File": np.unicode, "Count": np.int})
        num_frames_info = train_df["Count"].values
        assert (len(num_frames_info) == len(in_audios))

    for i, in_audio in enumerate(in_audios):
        if not out_files[i]:
            file_stem, _ = os.path.splitext(os.path.basename(in_audio))
            out_files[i] = os.path.join(output_dir, file_stem + ".npy")
            # print(out_files[i])
            
    conv_audios_to_deepspeech(
        audios=in_audios,
        out_files=out_files,
        num_frames_info=num_frames_info,
        deepspeech_pb_path=deepspeech_pb_path)

def process_audio_files(audio_file_paths, deepspeech_pb_path, metainfo_file_path):
    out_file_paths = [os.path.splitext(path)[0] + ".npy" for path in audio_file_paths]
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(extract_features, audio_file_paths, out_file_paths, [deepspeech_pb_path]*len(audio_file_paths), [metainfo_file_path]*len(audio_file_paths))

def main():
    """
    Main body of script.
    """
    # args.deepspeech = '~/.tensorflow/models/deepspeech-0_1_0-b90017e8.pb'
    args = parse_args()
    in_audio = os.path.expanduser(args.input)
    if not os.path.exists(in_audio):
        raise Exception(f"Input file/directory doesn't exist: {in_audio}")

    deepspeech_pb_path = get_deepspeech_model_file() if args.deepspeech is None else os.path.expanduser(args.deepspeech)
    if not os.path.exists(deepspeech_pb_path):
        raise FileNotFoundError(f"DeepSpeech model file not found: {deepspeech_pb_path}")

    output_dir = args.output if args.output else os.getcwd()
    if os.path.isfile(in_audio):
        out_file = os.path.join(output_dir, os.path.basename(in_audio).replace('.wav', '.npy'))
        extract_features(
            in_audios=[in_audio],
            out_files=[out_file],
            deepspeech_pb_path=deepspeech_pb_path,
            output_dir=output_dir,
            metainfo_file_path=args.metainfo)
    else:
        audio_file_paths = [os.path.join(in_audio, f) for f in os.listdir(in_audio) if f.lower().endswith('.wav')]
        out_file_paths = [os.path.join(output_dir, os.path.basename(path).replace('.wav', '.npy')) for path in audio_file_paths]
        extract_features(
            in_audios=audio_file_paths,
            out_files=out_file_paths,
            deepspeech_pb_path=deepspeech_pb_path,
            output_dir=output_dir,
            metainfo_file_path=args.metainfo)


if __name__ == "__main__":
    main()

