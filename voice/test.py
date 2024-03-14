#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from argparse import RawTextHelpFormatter
# pylint: disable=redefined-outer-name, unused-argument
from pathlib import Path
import sys
#sys.path.append("/home/ubuntu/home/TTS")
from TTS.utils.manage import ModelManager
from TTS.utils.synthesizer import Synthesizer


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    if v.lower() in ("no", "false", "f", "n", "0"):
        return False
    raise argparse.ArgumentTypeError("Boolean value expected.")

def main():
    #path = Path(__file__).parent / "TTS/.models.json"
    #manager = ModelManager(path, progress_bar=args.progress_bar)
    tts_path = "/home/ubuntu/home/yourtts-pth-version2/model_file.pth"
    tts_config_path = "/home/ubuntu/home/yourtts-pth-version2/config.json"
    speakers_file_path = None
    language_ids_file_path = None
    vocoder_path = None
    vocoder_config_path = None
    encoder_path = None
    encoder_config_path = None
    vc_path = None
    vc_config_path = None
    use_cuda = True
    synthesizer = Synthesizer(
        tts_path,
        tts_config_path,
        speakers_file_path,
        language_ids_file_path,
        vocoder_path,
        vocoder_config_path,
        encoder_path,
        encoder_config_path,
        vc_path,
        vc_config_path,
        use_cuda,
    )
    text = "我是丁真，知识海豹。女士们先生们大家好。"
    if tts_path is not None:
        wav = synthesizer.tts(
            text,
            speaker_wav="/home/ubuntu/wave/235628482-1-208.mp4",
        )
    out_path = "/home/ubuntu/wave/a.wav"
    print(" > Saving output to {}".format(out_path))
    synthesizer.save_wav(wav, out_path)


if __name__ == "__main__":
    main()