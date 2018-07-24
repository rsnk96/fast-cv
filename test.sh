#!/bin/bash


# If no parameters are supplied, INPUT_VIDEO is a blank string
if [ ! $# -eq 0 ]; then
    INPUT_VIDEO="--input_file=$@";
fi

python 1-traditional_cv.py $INPUT_VIDEO
python 1-traditional_cv.py $INPUT_VIDEO --x264=True
python 1-traditional_cv.py $INPUT_VIDEO --x264=True --extra_flags="-preset ultrafast"
echo "=================================="
python 2-multiproc_cv.py $INPUT_VIDEO
python 2-multiproc_cv.py $INPUT_VIDEO --extension="mp4"
python 2-multiproc_cv.py $INPUT_VIDEO --extension="mp4" --extra_flags="-preset ultrafast"
python 2-multiproc_cv.py $INPUT_VIDEO --extension="mp4" --x264=True
python 2-multiproc_cv.py $INPUT_VIDEO --extension="mp4" --x264=True --extra_flags="-preset ultrafast"
echo "=================================="
python 3-multiproc_pipe_to_hdd_ffmpeg.py $INPUT_VIDEO
python 3-multiproc_pipe_to_hdd_ffmpeg.py $INPUT_VIDEO --extra_flags="-preset ultrafast"
python 3-multiproc_pipe_to_hdd_ffmpeg.py $INPUT_VIDEO --part_extension="ts"
python 3-multiproc_pipe_to_hdd_ffmpeg.py $INPUT_VIDEO --part_extension="ts" --extra_flags="-preset ultrafast"
echo "=================================="
python 4-multiproc_pipe_to_stream_ffmpeg.py $INPUT_VIDEO
python 4-multiproc_pipe_to_stream_ffmpeg.py $INPUT_VIDEO  --extra_flags="-preset ultrafast"
echo "=================================="
