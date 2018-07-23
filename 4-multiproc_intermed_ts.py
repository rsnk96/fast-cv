import cv2
import sys
import time
import subprocess as sp
import multiprocessing as mp


start_time = time.time()

if len(sys.argv) > 1:
    input_file = sys.argv[1]
else:
    input_file = 'Kiiara.mp4'

num_processes = mp.cpu_count()
cap = cv2.VideoCapture(input_file)
frame_jump_unit = cap.get(cv2.CAP_PROP_FRAME_COUNT)//num_processes
width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
cap.release()

def process_video(group_number):
    cap = cv2.VideoCapture(input_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump_unit*group_number)
    proc_frames=0
    pipe = sp.Popen( command+['{}.ts'.format(group_number)], stdin=sp.PIPE, stderr=sp.PIPE)
    while (proc_frames < frame_jump_unit):
        ret, frame = cap.read()
        if ret == False:
            break
        # print(cap.get(cv2.CAP_PROP_POS_FRAMES))
        frame[:height//2, :width//2, 1:] = 0
        frame[:height//2, width//2:, [2,0]] = 0
        frame[height//2:, width//2:, :2] = 0
        pipe.stdin.write(frame.tobytes())
        proc_frames += 1

    cap.release()
    pipe.communicate(b'q')  # ffmpeg closes the stream on entering 'q'
    return None

FFMPEG_BIN = "ffmpeg" # on Linux ans Mac OS
command = [ FFMPEG_BIN,
        '-y', # (optional) overwrite output file if it exists
        '-loglevel', 'warning',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', '{}x{}'.format(width,height), # size of one frame
        '-pix_fmt', 'bgr24',
        '-r', str(fps), # frames per second
        '-i', '-', # The imput comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'libx264']
p = mp.Pool(num_processes)
p.map(process_video, range(num_processes))

transport_streams=['{}.ts'.format(i) for i in range(num_processes)]
with open('intermediate_files.txt', 'w') as f:
    for t in transport_streams:
        f.write('file {}\n'.format(t))

sp.Popen('ffmpeg -y -f mpegts -loglevel warning -i \"concat:{}\" -an -vcodec copy -preset ultrafast output_method4.mp4'.format('|'.join(transport_streams)), shell=True).wait()
from os import remove
for f in transport_streams:
    remove(f)

t2 = time.time()


FFMPEG_BIN = "ffmpeg" # on Linux ans Mac OS
command = [ FFMPEG_BIN,
        '-y', # (optional) overwrite output file if it exists
        '-loglevel', 'warning',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', '{}x{}'.format(width,height), # size of one frame
        '-pix_fmt', 'bgr24',
        '-r', str(fps), # frames per second
        '-i', '-', # The imput comes from a pipe
        '-an', # Tells FFMPEG not to expect any audio
        '-vcodec', 'libx264',
        '-preset', 'ultrafast']
p = mp.Pool(num_processes)
p.map(process_video, range(num_processes))

transport_streams=['{}.ts'.format(i) for i in range(num_processes)]
with open('intermediate_files.txt', 'w') as f:
    for t in transport_streams:
        f.write('file {}\n'.format(t))

sp.Popen('ffmpeg -y -f mpegts -loglevel warning -i \"concat:{}\" -an -vcodec copy -preset ultrafast output_method4.mp4'.format('|'.join(transport_streams)), shell=True).wait()
from os import remove
for f in transport_streams:
    remove(f)

t3 = time.time()

print('Method {}: Time taken default: {} and ultrafast preset:{}\n\n'.format(sys.argv[0], t2-start_time, t3-t2))