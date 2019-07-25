#
# MIT License
#
# Copyright (c) 2019 Keisuke Sehara
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import subprocess as _sp
import argparse
from pathlib import Path as _Path
import sys as _sys
import os as _os
import math as _math
from traceback import print_exc as _print_exc
from skvideo.io import FFmpegReader as _VReader, FFmpegWriter as _VWriter

VERSION_STR="1.0alpha"
DEFAULT_TARGET=2000000000

parser = argparse.ArgumentParser(description='split a video file into smaller files.')
parser.add_argument("input_files", nargs='+',
                    help="can be any video files that ffmpeg accepts.")
parser.add_argument("--target", type=int, default=DEFAULT_TARGET,
                    help=f"target file size which each of the output files shall not exceed."+
                    "defaults to {DEFAULT_TARGET} bytes (1.9 GB).")

class ProcessingError(RuntimeError):
    def __init__(self, msg):
        super().__init__(msg)

class FragmentWriter:
    
    @classmethod
    def iterate(cls, number, basename="video", outputdir=_Path(), suffix='.mp4', verbose=True):
        index = 0
        while index < number:
            index += 1
            path   = outputdir / f"{basename}_{index:03d}{suffix}"
            yield cls(path, verbose=verbose)

    def __init__(self, path, verbose=True):
        self.writer  = _VWriter(str(path))
        self.path    = path
        self.verbose = verbose
        self.count   = 0

    def write(self, frame):
        self.writer.writeFrame(frame)
        self.count  += 1

    def __enter__(self):
        if self.verbose == True:
            print(f">>> writing to: {self.path}...", end='', flush=True)
        return self

    def __exit__(self, typ, val, tb):
        self.writer.close()
        if self.verbose == True:
            print(f"done ({self.count} frames).", flush=True)
        return val if typ is not None else True


def get_frame_count(path):
    ret = _sp.run(["ffprobe",
                   "-v", "error",
                   "-count_frames",
                   "-select_streams", "v:0",
                   "-show_entries", "stream=nb_read_frames",
                   "-of", "default=nokey=1:noprint_wrappers=1",
                   str(path)],
                  capture_output=True)
    if ret.returncode == 0:
        return int(ret.stdout.decode('utf-8').strip())
    else:
        raise RuntimeError(ret)

def rough_size(siz):
    units = ('bytes', 'kB', 'MB', 'GB')
    for up, unit in enumerate(units):
        if siz < 1500:
            if isinstance(siz, int):
                return f"{siz}{unit}"
            else:
                return f"{siz:.1f}{unit}"
        else:
            siz = siz / 1024
    return f"{siz:.1f}TB"

def estimate_frame_per_file(path, target, verbose=True):
    """returns (frame_count, number_of_frames_per_file) in a tuple."""
    if verbose == True:
        print(f"[{path}]")
        print(">>> reading...", flush=True)
    siz   = _os.path.getsize(path)
    rsiz  = rough_size(siz)
    count = get_frame_count(path)
    per_frame = siz / count
    rpf   = rough_size(per_frame)
    rtg   = rough_size(target)
    estimate = int(target // per_frame)
    nfiles   = _math.ceil(count / estimate)
    if verbose == True:
        print(f"        frame-count = {count}")
        print(f"          file-size = {rsiz} ({rpf} per frame)")
        print(f"        target-size = {rtg}")
        print(f"    frames-per-file = {estimate}")
        print(f"    number-of-files = {nfiles}", flush=True)
    return count, estimate, nfiles

def process_file(path, target, verbose=True):
    path = _Path(path)
    if not path.is_file():
        raise ProcessingError(f"not a file: {path}")

    try:
        total_count, per_file, nfiles = estimate_frame_per_file(path, target, verbose=verbose)
    except:
        _print_exc()
        raise ProcessingError(f"running of ffprobe failed")

    if per_file < 10:
        raise ProcessingError("target file size seems to be too small")
    elif per_file >= total_count:
        raise ProcessingError(f"no need to split {path}")

    # split the video
    outputpath = path.with_suffix(".split")
    if outputpath.exists():
        if not outputpath.is_dir():
            raise ProcessingError(f"file exists in place of the output directory: {outputpath}")
        else:
            pass # overwrite existing .split directory
    else:
        outputpath.mkdir(parents=True)

    source = iter(_VReader(str(path)).nextFrame())
    try:
        frame = next(source) # always read the next frame before
                             # so that we don't have to create an empty fragment
        for j, fragment in enumerate(FragmentWriter.iterate(nfiles,
                                                        basename=path.stem,
                                                        outputdir=outputpath,
                                                        verbose=verbose)):
            with fragment as out:
                for i in range(per_file):
                    out.write(frame)
                    frame = next(source)
    except StopIteration:
        pass
    if verbose == True:
        print(f">>> split into {j+1} files.")

def run(input_files=[], target=None, verbose=True):
    if target is None:
        target = DEFAULT_TARGET
    for path in input_files:
        try:
            process_file(path, target, verbose=verbose)
        except ProcessingError as e:
            print(f"***{e}", file=_sys.stderr, flush=True)
            continue
        except:
            _print_exc()
            print(f"***failed to process: {path}", file=_sys.stderr, flush=True)
            continue


