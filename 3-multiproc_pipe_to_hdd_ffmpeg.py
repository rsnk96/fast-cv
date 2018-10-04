import cv2
import sys
import time
import argparse
import numpy as np
import subprocess as sp
import multiprocessing as mp


def process_video(group_number):
    cap = cv2.VideoCapture(args.input_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)
    proc_frames = 0
    pipe = sp.Popen(
        command + ["{}.{}".format(group_number, args.part_extension)],
        stdin=sp.PIPE,
        stderr=sp.PIPE,
    )
    while proc_frames < frame_jump_unit:
        ret, frame = cap.read()
        if ret == False:
            break
        pipe.stdin.write(cv2.filter2D(frame, -1, kernel).tobytes())
        proc_frames += 1

    cap.release()
    pipe.communicate(b"q")  # ffmpeg closes the stream on entering 'q'
    return None

if __name__ == '__main__':
    kernel = np.ones((5,5),np.float32)/25
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default="Kiiara.mp4", type=str)
    parser.add_argument("--part_extension", choices=["mp4", "ts"], default="mp4")
    parser.add_argument("--extra_flags", default="", type=str)
    args = parser.parse_args()

    start_time = time.time()
    num_processes = mp.cpu_count()
    cap = cv2.VideoCapture(args.input_file)
    frame_jump_unit = cap.get(cv2.CAP_PROP_FRAME_COUNT) // num_processes
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

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
        "-i", "-",  # The input comes from a pipe
        "-an",  # Tells FFMPEG not to expect any audio
        "-vcodec", "libx264" ]
    command.extend(args.extra_flags.split())
    
    p = mp.Pool(num_processes)
    p.map(process_video, range(num_processes))


    transport_streams = ["{}.{}".format(i, args.part_extension) for i in range(num_processes)]
    with open("intermediate_files.txt", "w") as f:
        for t in transport_streams:
            f.write("file {} \n".format(t))

    if args.part_extension == "mp4":
        ffmpeg_joining_command = "ffmpeg -y -loglevel warning -f concat -safe 0 -i intermediate_files.txt -c copy {} output_method3.mp4".format(
            args.extra_flags
        )
    else:
        ffmpeg_joining_command = 'ffmpeg -y -f mpegts -loglevel warning -i "concat:{}" -an -vcodec copy {} output_method3.mp4'.format(
            "|".join(transport_streams), args.extra_flags
        )

    t2 = time.time()
    sp.Popen(ffmpeg_joining_command, shell=True).wait()
    t3 = time.time()

    from os import remove

    for f in transport_streams:
        remove(f)
    remove("intermediate_files.txt")

    print(
        "Method {}: Input:{}, Part_extension:{}, extra_flags:{}, Time taken: {}".format(
            sys.argv[0], args.input_file, args.part_extension, args.extra_flags, t3 - start_time
        )
    )
