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
    out = cv2.VideoWriter('{}.mkv'.format(group_number),cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height)) 
    while (proc_frames < frame_jump_unit):
        ret, frame = cap.read()
        if ret == False:
            break
        frame[:height//2, :width//2, 1:] = 0
        frame[:height//2, width//2:, [2,0]] = 0
        frame[height//2:, width//2:, :2] = 0
        out.write(frame)
        proc_frames += 1

    cap.release()
    out.release()
    return None

p = mp.Pool(num_processes)
p.map(process_video, range(num_processes))

transport_streams=['{}.mkv'.format(i) for i in range(num_processes)]
with open('intermediate_files.txt', 'w') as f:
    for t in transport_streams:
        f.write('file {} \n'.format(t))

t2 = time.time()
sp.Popen('ffmpeg -y -loglevel warning -f concat -safe 0 -i intermediate_files.txt -c copy output_method5.mp4', shell=True).wait()
t3 = time.time()
sp.Popen('ffmpeg -y -loglevel warning -f concat -safe 0 -i intermediate_files.txt -c copy -preset ultrafast output_method5.mp4', shell=True).wait()
t4 = time.time()

from os import remove
for f in transport_streams:
    remove(f)
remove('intermediate_files.txt')

print('Method {}: Time taken default: {} and ultrafast preset:{}\n\n'.format(sys.argv[0], t3-start_time, t4-t3+t2-start_time))