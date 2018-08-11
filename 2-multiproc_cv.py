import cv2
import sys
import time
import argparse
import subprocess as sp
import multiprocessing as mp
from docopt import docopt


def process_video(group_number):
    cap = cv2.VideoCapture(args.input_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)
    proc_frames = 0
    out = cv2.VideoWriter(
        "{}.{}".format(group_number, args.extension),
        cv2.VideoWriter_fourcc(*vid_fourcc[args.extension]),
        fps,
        (width, height),
    )

    while proc_frames < frame_jump_unit:
        ret, frame = cap.read()
        if ret == False:
            break
        frame[: height // 2, : width // 2, 1:] = 0
        frame[: height // 2, width // 2 :, [2, 0]] = 0
        frame[height // 2 :, width // 2 :, :2] = 0
        out.write(frame)
        proc_frames += 1

    cap.release()
    out.release()
    return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default="Kiiara.mp4", type=str)
    parser.add_argument("--x264", default=False, type=bool)
    parser.add_argument("--extension", choices=["mp4", "avi", "mkv"], default="avi")
    parser.add_argument("--extra_flags", default="", type=str)
    args = parser.parse_args()
    start_time = time.time()
    
    num_processes = mp.cpu_count()
    vid_fourcc = {"avi": "MJPG", "mp4": "mp4v", "mkv": "mp4v"}
    cap = cv2.VideoCapture(args.input_file)
    frame_jump_unit = cap.get(cv2.CAP_PROP_FRAME_COUNT) // num_processes
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    p = mp.Pool(num_processes)
    p.map(process_video, range(num_processes))

    intermediate_files = ["{}.{}".format(i, args.extension) for i in range(num_processes)]
    with open("intermediate_files.txt", "w") as f:
        for t in intermediate_files:
            f.write("file {} \n".format(t))

    ffmpeg_command = "ffmpeg -y -loglevel error -f concat -safe 0 -i intermediate_files.txt {}".format(
        args.extra_flags
    ).strip()
    if args.x264 == False:
        ffmpeg_command += " -vcodec copy"
    else:
        ffmpeg_command += " -vcodec libx264"
    ffmpeg_command += " output_method2.{}".format(args.extension)
    t2 = time.time()
    sp.Popen(ffmpeg_command, shell=True).wait()
    t3 = time.time()

    from os import remove

    for f in intermediate_files:
        remove(f)
    remove("intermediate_files.txt")
    print(
        "Method {}: Input:{}, re-encode to x264:{}, output extension:{}, extra_flags:{}, Time taken: {}".format(
            sys.argv[0], args.input_file, args.x264, args.extension, args.extra_flags, t3 - start_time
        )
    )