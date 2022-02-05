#!/usr/bin/env python

import argparse
import os
import subprocess
import platform
import signal
import filetype

from playsound import playsound

SYRO_SCRIPT = "syro_volcasample_example.%s" % platform.machine()
CWD = os.getcwd()
FULL_PATH_SCRIPT = os.path.join(CWD, "bin", SYRO_SCRIPT)


def is_wav(directory, file_name):
    if ".wav" in file_name:
        return True

    full_path = os.path.join(directory, file_name)
    kind = filetype.guess(full_path)
    if kind and kind.extension == 'wav':
        return True

    return False


def upload_dir(directory):
    for i, file_name in enumerate([fname
                                   for fname in os.listdir(directory)
                                   if is_wav(directory, fname)]):
        if i > 99:
            break

        base_name, ext = os.path.splitext(file_name)
        full_path = os.path.join(directory, file_name)

        tmp_file = f"{i:0>3}-{base_name}-stream.wav"
        proc = subprocess.Popen(
            [f"{FULL_PATH_SCRIPT}", f"{tmp_file}", f"s{i}c:{full_path}"]
        )
        proc.wait()

        playsound(tmp_file)
        os.remove(tmp_file)


def clear_samples():
    for i in range(100):
        clr_out = f"{i:0>3}-stream_clr.wav"
        proc = subprocess.Popen([f"{FULL_PATH_SCRIPT}", f"{clr_out}", f"e{i}:"])
        proc.wait()

        playsound(clr_out)

        os.remove(clr_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="gnuvolca",
        description="""
        Korg Volca Sample uploader for linux.
        Detects all .wav files in the specified directory, converts and reproduces all file uploads.
        """
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-d", "--dir",
        type=str,
        help="Path to directory containing samples to be uploaded"
    )
    group.add_argument(
        "-c", "--clear",
        action=argparse._StoreTrueAction,
        help="Pass this for erasing all samples on the Volca Sample"
    )
    args = parser.parse_args()

    try:
        if args.clear:
            clear_samples()
        else:
            upload_dir(args.dir)
    except KeyboardInterrupt:
        for line in os.popen("ps aux | grep playsound | grep -v grep | awk '{ print $2 }'"):
            os.kill(int(line.strip()), signal.SIGKILL)
