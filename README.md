# video-file-splitter

a tool to split a large (e.g. >2 GB) video file into smaller (e.g. <~2 GB) ones.

## Dependencies

1. `ffmpeg`, including the `ffprobe` program: for the Mac or Linux, the use of 
   some package manager (e.g. `apt` or `brew`) may be a lot easier.
2. `scikit-video`: can be installed via `pip install scikit-video`.

## Installation

Use `pip` to install directly from GitHub:

```
$ pip install git+https://github.com/gwappa/video-file-splitter.git
```

Alternatively, you can clone the Git repository and then locally install:

```
$ git clone https://github.com/gwappa/video-file-splitter.git
$ cd video-file-splitter
$ pip install .
```

## Running

Run `videosplitter --help` to see what arguments can be used.

## License

The MIT license.

