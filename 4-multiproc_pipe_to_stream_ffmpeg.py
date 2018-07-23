import os
import cv2
import sys
import time
import psutil
import argparse
import subprocess as sp
import multiprocessing as mp


# encode_buf_size = psutil.virtual_memory()[4]*0.5//num_processes
def process_video(group_number):
    cap = cv2.VideoCapture(args.input_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)
    proc_frames = 0
    FIFO_PATH = FIFO_PATHs[group_number]
    pipe = sp.Popen(
        command + [FIFO_PATH], stdin=sp.PIPE, stderr=sp.PIPE
    )  # Adding the FIFO_PATH makes ffmpeg redirect the output to the appropriate pipe
    while proc_frames < frame_jump_unit:
        ret, frame = cap.read()
        if ret == False:
            break
        frame[: height // 2, : width // 2, 1:] = 0
        frame[: height // 2, width // 2 :, [2, 0]] = 0
        frame[height // 2 :, width // 2 :, :2] = 0
        # print('{} '.format(cap.get(cv2.CAP_PROP_POS_FRAMES)))
        pipe.stdin.write(frame.tobytes())
        pipe.stdin.flush()
        # print('test', group_number)
        proc_frames += 1

    cap.release()
    pipe.communicate(b"q")  # ffmpeg closes the stream on entering 'q'
    os.unlink(FIFO_PATH)
    return None


if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default="Kiiara.mp4", type=str)
    parser.add_argument("--extra_flags", default="", type=str)
    args = parser.parse_args()
    num_processes = mp.cpu_count()

    cap = cv2.VideoCapture(args.input_file)
    frame_jump_unit = cap.get(cv2.CAP_PROP_FRAME_COUNT) // num_processes
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    FIFO_PATHs = tuple("/tmp/my_fifo_{}".format(i) for i in range(num_processes))
    for FIFO_PATH in FIFO_PATHs:
        if os.path.exists(FIFO_PATH):
            os.unlink(FIFO_PATH)
        os.mkfifo(FIFO_PATH)

    FFMPEG_BIN = "ffmpeg"  # on Linux ans Mac OS
    command = [
        FFMPEG_BIN,
        "-y",  # (optional) overwrite output file if it exists
        "-loglevel", "warning",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "{}x{}".format(width, height),  # size of one frame
        "-pix_fmt", "bgr24",
        "-r", str(fps),  # frames per second
        "-i", "-",  # The imput comes from a pipe
        "-an",  # Tells FFMPEG not to expect any audio
        "-r", str(fps),
        "-vcodec", "libx264",
        "-f", "mpegts", ]
    command.extend(args.extra_flags.split())

    p = mp.Pool(num_processes)
    r = p.map_async(process_video, range(num_processes))

    sp.Popen(
        'ffmpeg -y -loglevel warning -f mpegts -i "concat:{}" -an -vcodec copy -use_wallclock_as_timestamps 1 {} output_method4.mp4'.format(
            "|".join(FIFO_PATHs), args.extra_flags
        ),
        shell=True,
    )
    r.wait()

    t2 = time.time()

    print(
        "Method {}: Input:{}, extra_flags:{}, Time taken: {}".format(
            sys.argv[0], args.input_file, args.extra_flags, t2 - start_time
        )
    )