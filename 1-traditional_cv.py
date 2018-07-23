import cv2
import sys
import numpy as np
from subprocess import Popen
import time


start_time = time.time()

if len(sys.argv)>1:
    cap = cv2.VideoCapture(sys.argv[1])
else:
    cap = cv2.VideoCapture('Kiiara.mp4')

width, height, end_frame = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),cap.get(cv2.CAP_PROP_FRAME_COUNT)
if len(sys.argv)>2:
    cap.set(cv2.CAP_PROP_POS_FRAMES, sys.argv[2])
    end_frame=sys.argv[3]


out = cv2.VideoWriter('output_method1.avi',cv2.VideoWriter_fourcc(*'MJPG'), cap.get(cv2.CAP_PROP_FPS), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))) 

while(cap.isOpened()):
    ret,frame = cap.read()
    if ret==False:
        break
    frame[:height//2, :width//2, 1:] = 0
    frame[:height//2, width//2:, [2,0]] = 0
    frame[height//2:, width//2:, :2] = 0
    out.write(frame)

cap.release()
out.release()

t2 = time.time()
Popen('ffmpeg -y -loglevel warning -i output_method1.avi -vcodec libx264 output_method1.mp4', shell=True).wait()
t3 = time.time()
Popen('ffmpeg -y -loglevel warning -i output_method1.avi -vcodec libx264 -preset ultrafast output_method1.mp4', shell=True).wait()
t4 = time.time()

print('Method {}: Time taken avi output: {} and mp4 output:{} and ultrafast mp4 output:{}\n\n'.format(sys.argv[0], t2-start_time, t3-start_time, t4-t3+t2-start_time))