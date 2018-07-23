python 1-traditional_cv.py
python 1-traditional_cv.py --x264=True
python 1-traditional_cv.py --x264=True --extra_flags="-preset ultrafast"
echo "=================================="
python 2-multiproc_cv.py
python 2-multiproc_cv.py --extension="mp4"
python 2-multiproc_cv.py --extension="mp4" --extra_flags="-preset ultrafast"
python 2-multiproc_cv.py --extension="mp4" --x264=True
python 2-multiproc_cv.py --extension="mp4" --x264=True --extra_flags="-preset ultrafast"
echo "=================================="
python 3-multiproc_pipe_to_hdd_ffmpeg.py
python 3-multiproc_pipe_to_hdd_ffmpeg.py --extra_flags="-preset ultrafast"
python 3-multiproc_pipe_to_hdd_ffmpeg.py --part_extension="ts"
python 3-multiproc_pipe_to_hdd_ffmpeg.py --part_extension="ts" --extra_flags="-preset ultrafast"
echo "=================================="
python 4-multiproc_pipe_to_stream_ffmpeg.py
python 4-multiproc_pipe_to_stream_ffmpeg.py  --extra_flags="-preset ultrafast"
echo "=================================="
