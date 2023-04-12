#!/usr/bin/env python
"""
Upload and manage WAV files on a Korg Volca Sample device using Linux systems.

This module provides a command-line interface for uploading WAV files to a Korg
Volca Sample device on Linux systems. It processes WAV files in the specified
directory, converts them using the syro_volcasample_example script, and plays
the converted samples. It also provides an option to clear all samples from the
Volca Sample device.

Usage:
gnuvolca -d <directory> # Upload WAV files from the specified directory
gnuvolca -c # Clear all samples from the Volca Sample device

Functions:
main(directory) : Process and upload WAV files in the specified directory
clear_samples() : Clear all samples from the Volca Sample device
"""

import time
import argparse
import os
import logging
import subprocess
import platform
import signal

from playsound import playsound
from alive_progress import alive_bar

SYRO_SCRIPT = "syro_volcasample_example.%s" % platform.machine()
CWD = os.getcwd()
FULL_PATH_SCRIPT = os.path.join(CWD, "bin", SYRO_SCRIPT)


def main(directory):
    """
    Process WAVs in directory and upload to Korg Volca Sample.

    This function iterates through the provided directory and its
    subdirectories, searching for WAV files. For each WAV file found, it calls
    the syro_volcasample_example script to convert and prepare the sample for
    uploading. The converted sample is then played using playsound and deleted
    from the filesystem.

    Args:
        directory (str): The path to the directory containing the WAV files to
        be processed.

    Raises:
        ValueError: If more than 100 WAV files are found in the
        specified directory.
    """
    logging.info("Processing and uploading samples")
    for root, dir, files in os.walk(directory):
        with alive_bar(len(files)) as progress_bar:

            for i, file in enumerate([file for file in files
                                      if ".wav" in file]):
                if i > 100:
                    raise ValueError("More than 100 samples in specified \
                        directory. Max limit 100.")

                filename = str(file).split(".", maxsplit=1)[0]
                file_out = f"{i:0>3}-{filename}-stream.wav"

                proc = subprocess.Popen([f"{FULL_PATH_SCRIPT}",
                                         f"{file_out}",
                                         f"s{i}c:{directory}{filename}.wav"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                proc.wait()
                out, err = proc.communicate()

                playsound(f"{file_out}")
                time.sleep(1)
                os.remove(file_out)

                print(out.decode('utf-8').strip(), end='\r')
                progress_bar()


def clear_samples():
    """
    Clear all 100 sample slots on the Korg Volca Sample.

    This function generates temporary WAV files for each of the 100 sample
    slots, calls the syro_volcasample_example script to create a file with
    an empty sample, and plays the sound using playsound.
    The temporary file is then removed.
    """
    logging.info("Clearing all sample slots")
    with alive_bar(100) as progress_bar:
        for i in range(100):
            clr_out = f"{i:0>3}-stream_clr.wav"

            proc = subprocess.Popen([f"{FULL_PATH_SCRIPT}",
                                     f"{clr_out}",
                                     f"e{i}:"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            proc.wait()
            out, err = proc.communicate()

            playsound(clr_out)
            os.remove(clr_out)

            print(out.decode('utf-8').strip(), end='\r')
            progress_bar()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('alive_progress')

    parser = argparse.ArgumentParser(
        prog="gnuvolca",
        description="""
        Korg Volca Sample uploader for linux.
        Detects all .wav files in the specified directory, converts and
        reproduces all file uploads.
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
