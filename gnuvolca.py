#!/usr/bin/env python

import argparse
import os
import struct
import subprocess
import platform
import signal
import filetype

from playsound import playsound

SYRO_SCRIPT = "syro_volcasample_example.%s" % platform.machine()
CWD = os.getcwd()
FULL_PATH_SCRIPT = os.path.join(CWD, "bin", SYRO_SCRIPT)


def get_vsj_samples(vsj_file):
    WRONG_MAGIC_ERROR = "Wrong magic number, wrong format of corrupted file"

    root_directory = os.path.dirname(vsj_file)
    samples_directory = os.path.join(root_directory, 'samples')
    samples_file = os.path.join(root_directory, 'samples/samples')

    with open(samples_file, 'rb') as f:
        binary = f.read()

    header, = struct.unpack('<I', binary[:4])
    assert header == 1414745427, WRONG_MAGIC_ERROR
    binary = binary[4:]

    block_struct = struct.Struct("100s B 10x 100s 4x")
    block_size = block_struct.size

    for i in range(100):
        block = binary[:block_size]
        binary = binary[block_size:]

        sample_name, has_wav, file_name = block_struct.unpack(block)
        sample_name = sample_name.decode('utf-8').replace(chr(0), '')
        file_name = file_name.decode('utf-8').replace(chr(0), '')
        has_wav = bool(has_wav)

        if has_wav:
            yield samples_directory, file_name
        else:
            yield samples_directory, ''

    footer, = struct.unpack('<I', binary[:4])
    assert footer == 1145392467, WRONG_MAGIC_ERROR


def is_wav(directory, file_name):
    if ".wav" in file_name:
        return True

    full_path = os.path.join(directory, file_name)
    kind = filetype.guess(full_path)
    if kind and kind.extension == 'wav':
        return True

    return False


def upload_file(directory, file_name, i=0):
    print(directory, file_name, i)
    base_name, ext = os.path.splitext(file_name)
    full_path = os.path.join(directory, file_name)

    tmp_file = f"{i:0>3}-{base_name}-stream.wav"
    proc = subprocess.Popen(
        [f"{FULL_PATH_SCRIPT}", f"{tmp_file}", f"s{i}c:{full_path}"]
    )
    proc.wait()

    playsound(tmp_file)
    os.remove(tmp_file)


def clear_sample(i):
    clr_out = f"{i:0>3}-stream_clr.wav"
    proc = subprocess.Popen([f"{FULL_PATH_SCRIPT}", f"{clr_out}", f"e{i}:"])
    proc.wait()

    playsound(clr_out)
    os.remove(clr_out)


def upload_dir(directory):
    for i, file_name in enumerate([fname
                                   for fname in os.listdir(directory)
                                   if is_wav(directory, fname)]):
        if i > 99:
            break

        upload_file(directory, file_name, i)


def upload_vsj(vsj_file):
    for i, (directory, file_name) in enumerate(get_vsj_samples(vsj_file)):
        if file_name:
            upload_file(directory, file_name, i)
        else:
            clear_sample(i)


def clear_samples():
    for i in range(100):
        clear_sample(i)


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
        "--vsj",
        type=str,
        help="Vosyr project path"
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
            if args.dir:
                upload_dir(args.dir)
            elif args.vsj:
                upload_vsj(args.vsj)
            else:
                raise ValueError("You have to specify a sample directory or a .vsj file")

    except KeyboardInterrupt:
        for line in os.popen("ps aux | grep playsound | grep -v grep | awk '{ print $2 }'"):
            os.kill(int(line.strip()), signal.SIGKILL)
