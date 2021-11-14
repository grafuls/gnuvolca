#!/usr/bin/env python

import argparse
import os
import subprocess
import platform
import signal

from playsound import playsound

SYRO_SCRIPT = "syro_volcasample_example.%s" % platform.machine()
CWD = os.getcwd()
FULL_PATH_SCRIPT = os.path.join(CWD, "bin", SYRO_SCRIPT)


def main(directory):
    for root, dir, files in os.walk(directory):
        for i, file in enumerate([file for file in files if ".wav" in file]):
            if i > 100:
                break
            
            filename = str(file).split(".")[0]
            file_out = f"{i:0>3}-{filename}-stream.wav"
            
            proc = subprocess.Popen([f"{FULL_PATH_SCRIPT}", f"{file_out}", f"s{i}c:{directory}{filename}.wav"])
            proc.wait()

            playsound(f"{file_out}")
            
            os.remove(file_out)

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
            main(args.dir)
    except KeyboardInterrupt:
            for line in os.popen("ps aux | grep playsound | grep -v grep | awk '{ print $2 }'"):
                os.kill(int(line.strip()), signal.SIGKILL)
