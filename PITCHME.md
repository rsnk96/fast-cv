@title[Efficient Video Processing]
#### Piping the Parallelism out of Python
## Efficient Video Processing

<font size="5">R S Nikhil Krishna   @rsnk96
<br>
Lokesh Kumar T    @tlokeshkumar</font>
<br>
<font size="6">Follow the presentation @ <https://goo.gl/KM2GoR></font>

---
@transition[none]
@snap[north]
## Why Bother?
@snapend
* 2009: Youtube announces 1080p,      30  fps support
* 2015: Youtube announces  8k (4320p), 60  fps support
* 2016: AMD announces 16k(8640p), 240 fps VR support

<font size="1">AMD announces 16k support: https://www.tweaktown.com/news/53163/amd-radeon-pro-graphics-card-powers-16k-display-15-360-8640/index.html</font>


+++
@transition[fade]
## Why Bother?
`\begin{align}
\small{\text{Demand}} & = \tiny{\frac{(7680 \times 4320) \times 120 \ \text{[2018]} }{(1280 \times 720) \times 60 \ \text{[2009]} }} & = & 72\text{x} \\
\small{\text{Supply}} \tiny{\textrm{(HDD ~100 USD)}} & = \tiny{\frac{3 \ \textrm{TB} \quad \text{[2018]} }{500 \ \textrm{GB} \quad \text{[2009]} } } & = & 6\text{x} \\
\small{\text{Supply}} \tiny{\textrm{(CPU ~300 USD)}} & = \tiny{\frac{3.7\ \textrm{GHz} \times 16\  \textrm{Threads}\  \text{[2018]} }{2.9 \ \textrm{Ghz} \times 8\ \textrm{Threads} \ \text{[2009]} }} & = & 2.55\text{x} \\
\end{align}`

![shock](https://pa1.narvii.com/6913/8b28b2536160f3d35a3153febcc17ba792d6f28er1-500-271_hq.gif)

Note:
* This is not the full story, codecs compress this



+++
![comic-about-video-challenges](https://image.ibb.co/eMtG9K/vid_target.jpg)

Note:
* Programmer's dillemma


---
@title[Computer Vision]
# Computer Vision


+++?image=https://d.ibtimes.co.uk/en/full/1469739/vision-age-ultron.jpg
@ul
* @fa[desktop white] @color[white](Vision ?)
* @fa[times fa-3x white]
@ulend


+++
![image-to-pixels](https://media.giphy.com/media/YUxfQeQSLpCU0wT9fA/giphy.gif)

Note:
* First thought when video processing comes to your head: FFmpeg


+++
@title[FFmpeg]
# FFmpeg


+++
## FFmpeg 
* The Cross-Platform Multimedia Swiss-Knife
* Used by VLC, Youtube (controversial), etc
* Efficiently uses your hardware
    <div class="left">
    ![normal-cv-htop](https://preview.ibb.co/nCYV2z/normal_cv_htop.png)
    </div>
    <div class="right">
    ![ffmpeg-htop](https://image.ibb.co/kb0zvK/ffmpeg_htop.png)
    </div>
    
* Supports most modern day codecs

Note:
* Youtube controversy: FFmpeg has GPL license, so you don't need to openly claim that you use it. contributors to FFmpeg made a bug in the processing pipeline, not a fatal bug. Same bug shows up in FFmpeg too


+++
## Trouble in Paradise (@fa[times] Biryani)
* Adding a filter to ffmpeg is non-trivial
  * Lot of callback functions to define **in `C`**:
    ```python
    init(), uninit(), query_formats(), config_props(), filter_frame()
    ```
* @size[1](What if we want to do more than just adding a filter?)

<font size="2">Source: https://github.com/FFmpeg/FFmpeg/blob/master/doc/writing_filters.txt</font>

Note:
* Any industry dealing in just giving clients videos ==>  more than basic filters.
* ffmpeg accessible through terminal only==> pipe the data from numpy to ffmpeg from within Python


+++
## Pythonistas, Awake!!!!

<div class="left">
@ul
* Using Python, there's no limitation on the type of operations we can perform on videos
* Commonly used: OpenCV, Scikit-Image, PIL, etc
@ulend
</div>
<div class="right">
![python-meme](https://pvsmt99345.i.lithium.com/t5/image/serverpage/image-id/41242i1D8397BD21B07DA8/image-size/large?v=1.0&px=999)
</div>

Note:
* Best Part: No need to write it in C
* Next Slide: Codecs intro

+++
## Some Modern Codecs
<div class="left">
![x265-vs-VPx](https://www.extremetech.com/wp-content/uploads/2016/09/108157-Netflix-HEVC-ORG.png)
</div>
<div class="right">
![av1](https://cnet4.cbsistatic.com/img/2018/03/28/f9e54051-4fc0-4431-add8-22c75dd2a0f9/aomedia-av1-roadmap.jpg)
</div>
<font size=1>https://github.com/Netflix/vmaf</font>



+++?image=https://preview.ibb.co/dhLF3e/18_10_04_1020_477.png
### And OpenCV can encode NONE of them

Note:
* with its default backend


+++?image=https://preview.ibb.co/k7JHkK/h264.png
### @color[white](Which means a nice H265 frame)
+++
@transition[none]
<!-- .slide: data-background-image="https://preview.ibb.co/nBgbee/avi.png" data-transition="none" -->
### @color[white](Will end up looking like this instead)


+++
## The Middle Ground
<div class="left">
@ul
* Use Python for all the processing
* Pipe the numpy arrays arrays into FFmpeg to encode it using modern codecs
@ulend
</div>
<div class="right">
![python-meme2](https://i.imgflip.com/2jfs40.jpg)
</div>

+++
## Piping Numpy arrays into FFmpeg
Setting up the pipe for a `460`x`360` input in the format BGR,BGR,BGR
```python
command = [ 'ffmpeg',
          '-f', 'rawvideo', '-vcodec','rawvideo',
          '-s', '420x360', # size of one frame
          '-pix_fmt', 'bgr24',
          '-r', '24', # frames per second
          '-i', '-', # The imput comes from a pipe
          '-an', # Tells FFMPEG not to expect any audio
          '-vcodec', 'libx265',
          'my_output_videofile.mp4' ]

pipe = sp.Popen( command, stdin=sp.PIPE, stderr=sp.PIPE)
```


+++
## Piping Numpy arrays into FFmpeg
Now, to write frames,
```python
pipe = sp.Popen(command, stdin=sp.PIPE,stderr=sp.PIPE)
while (cap.isOpened()):
  ret, frame = cap.read()
  # Do some stuff
  pipe.proc.stdin.write( my_image_array.tostring() )
```

Read Zulko's (MoviePy) blog for more
<font size="2">Source: http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/</font>

Note:
* sp is subprocess lib
* What these 3 - 4 lines do: Let you access SotA codecs from within Python


+++
### The Problem
![comic-about-video-challenges](https://image.ibb.co/iJg8Oe/vid_target_ffmpeg_done.jpg)



---
@title[Parallelism in Video Processing]
# Parallelism in Video Processing


+++
<!-- .slide: data-background-image="https://i.imgflip.com/2jfpns.jpg" data-background-size="contain" -->

+++?image=https://media.giphy.com/media/pzAU8uEKFcRAsTjdKQ/giphy.gif
@ul
* @fa[times fa-4x black]
@ulend

Note:
* FFmpeg speeds up processing by parallelizing the processing of each frame, rather than parallelizing across frames. But parallelizing across frames is a much more fundamental approach, if you think about it, you handle each frame independently.
* Video compression is generally inter-frame, so we store some key frames and note how successive frames differ from the previous ones.


+++?image=https://media.giphy.com/media/2lh9grOpTCXnaP3zgw/giphy.gif

Note:
* take 10k frames as base


+++
### CV - The normal way
```python
  def process_video():
    cap = cv2.VideoCapture("input_file.mp4")
    out = cv2.VideoWriter("output_file.avi", ...)
    while (cap.isOpened()):
      ret, frame = cap.read()
      # ... DO SOME STUFF TO frame... #
      out.write(frame)
  
  process_video()
```


+++
### CV - The multiprocessing way
```python
  def process_video(group_number):
    cap = cv2.VideoCapture("input_file.mp4")
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump * group_number)
    proc_frames = 0
    out = cv2.VideoWriter("output_{}.avi".format(group_number), ...)
    while proc_frames < frame_jump:
      ret, frame = cap.read()
      # ... DO SOME STUFF TO frame ... #
      out.write(frame)
    return None

  import multiprocessing as mp
  num_processes = mp.cpu_count()
  num_frames = cv2.VideoCapture("input_file.mp4").get(cv2.CAP_PROP_FRAME_COUNT)
  frame_jump =  num_frames // num_processes

  p = mp.Pool(num_processes)
  p.map(process_video, range(num_processes))

  with open("temp_files.txt", "w") as f:
    for t in ["output_{}.avi".format(i) for i in range(num_processes)]:
      f.write("file {} \n".format(t))
  ffmpeg_command = "ffmpeg -f concat -safe 0 -i temp_files.txt -vcodec copy"
  sp.Popen(ffmpeg_command, shell=True).wait()
```


@[12-13](Number of parallel sub-processes)
@[14-15](Number of frames for each sub-process to process)
@[1-10](We modify the original function a bit)
@[1,3-6](The important changes)
@[17-18](And now we parallelize the processing of the video)
@[20-24](Merge the videos)


+++
The `# ... DO SOME STUFF ...` :
<div class="left">
![original-image](https://image.ibb.co/gvZmTe/normal.png)
</div>
<div class="right">
![changed-image](https://image.ibb.co/m5zaMz/convolved.png)
</div>

Note:
* Even for a small 640p video(pic), we can see significant speed-ups
* Speed up of ~2.3x on 2 core machine with just 10 extra lines of code
* Also note that in this method, we've completely stayed within Python, without coming out unlike piping into FFmpeg


+++
<canvas data-chart="bar">
<!-- 
{

 "data": {
  "labels": ["1-Core", "2-core, 2-hyperthreads"],
  "datasets": [
   {
    "data":[26.43, 12.87],
    "label":"mp4 ","backgroundColor":"rgba(237,101,101,.95)"
   }
  ]
 },
 "options": { 
    "responsive": "true",
    "title": {
      "display": true,
      "text": "Time to \"do some stuff\"",
      "fontColor": "gray",
      "fontSize": 20
    },
    "scales": {
      "xAxes": [{
        "scaleLabel": {
          "display": true,
          "labelString": "Method"
        }
      }],
      "yAxes": [{
        "ticks": {
            "beginAtZero": true
        },
        "scaleLabel": {
          "display": true,
          "labelString": "Time (sec)"
        }
      }]
    }
  }
}
-->
</canvas>



+++
<!-- .slide: data-background-image="https://i.imgflip.com/2jfpyk.jpg" data-background-size="contain" -->

### @color[white](Le crowd)

---?image=https://ksassets.timeincuk.net/wp/uploads/sites/54/2017/12/RvxjvHGLJgCCi7PkDEmMWP-970-80-920x517.jpg
@transition[none]
@title[GPU]
@snap[north-west headline]
@css[heading](Parallelism in Video Processing)
@snapend

@snap[south-east]
@color[white](GPU Parallelism)
@snapend

@snapend

+++
## Time-vs-Space

<font size="5">Whatever we've seen up till now is inter-frame parallelization</font>
![efficient-cpu-parallelism](https://media.giphy.com/media/2lh9grOpTCXnaP3zgw/giphy.gif)


+++?image=https://image.ibb.co/dZgSYe/18_10_04_546_519.png&size=auto 70%
@transition[none]
@snap[north]
Intra-Frame Parallelization
@snapend

+++
## Hidden Problems of parallelizing your video pipeline
@ul
* Reassembly of the video fragments in the correct order
* Assumption: Cores are powerful enough to process entire frames by themselves
@ulend


+++
## Program flow

![cuda-program-flow](https://www.researchgate.net/profile/Sorin_Zoican/publication/280038347/figure/fig3/AS:284600480878607@1444865450557/CUDA-program-flow.png)


+++
## Cuda Kernel
```python
@cuda.jit
def image_conv(ip_img, kernel, op_img, channels, w, h):
    r, c = cuda.grid(2) # Finding the global position of the thread
    
    kernel_c = cuda.const.array_like(conv_window)
    
    for b in range(BATCH):
        # Do some stuff
```
@[1](Decorator to make python function into a CUDA Kernel)
@[2](Function Header)
@[3](Find the global position of the thread)
@[5](Push the kernel to constant memory for faster read and write access)
@[7](Iterate over the batch of images)
@[8](Perform per frame processing ops)


+++
## GPU Memory Systems

@ul
* CPU Mem Access Speeds: RAM < Cache < Register
* GPU Mem Access Speeds: Global < Constant < Shared
@ulend



+++
## Shared Memory Optimizations

@ul
* On chip memory: Much faster access rates than global memory
* Latency: ~ 1/100x (uncached global memory latency)
* Load the part of input image used by a block into shared memory
* Read from shared memory for further computation in the kernel
@ulend

+++
## Using FFT for Image Convolution

![FFT-conv2d](https://i2.wp.com/khshim.files.wordpress.com/2016/10/fast-convolution-with-fft.png?resize=688%2C246&ssl=1)

<font size="2">Source: http://www.khshim.com/archives/681</font>

+++
## Streaming asynchronous streams
![nvidia-streams-cuda](https://devblogs.nvidia.com/wp-content/uploads/2012/11/C1060Timeline-1024x679.png)
<font size="2">Source: https://devblogs.nvidia.com/how-overlap-data-transfers-cuda-cc/</font>

+++

## Streaming asynchronous streams
@ul
- Implicit data transfers are blocking or synchronous transfers
- Kernel Launches are asynchronous
- Idea: Overlap kernel execution with data transfers each running in different streams.
@ulend

+++
### Streaming asynchronous streams

```python
for i in range(n_streams):
    streams.append(cuda.stream())

ip_img = cuda.device_array((n_streams, BATCH, rows, cols, 3))
op_img = cuda.device_array((n_streams, BATCH, rows, cols, 3))

for i, idx in enumerate(streams):
    ip_img[idx] = cuda.to_device(img_batch, stream=i)
    kernel[blockspergrid, threadsperblock, i](ip_img[idx], op_img[idx], ...)
    op_img_h = op_img[idx].copy_to_host(stream=i)
```
@[1-2](Creating the streams required for processing)
@[4-5](One way of alloting your input and output data arrays in GPU)
@[7](Iterate over the streams)
@[8-10](Do the require computation with **stream=i**)

+++
@title[Results - GPU]
<canvas data-chart="bar">
<!-- 
{

 "data": {
  "labels": ["1-Core", "2-core, 2-threads", "384 Cuda Cores, 4GB Global Memory"],
  "datasets": [
   {
    "data":[26.43, 12.87, 5.49],
    "label":"mp4 ","backgroundColor":"rgba(237,101,101,.95)"
   }
  ]
 },
 "options": { 
    "responsive": "true",
    "title": {
      "display": true,
      "text": "Time to \"do some stuff\"",
      "fontColor": "gray",
      "fontSize": 20
    },
    "scales": {
      "xAxes": [{
        "scaleLabel": {
          "display": true,
          "labelString": "Method"
        }
      }],
      "yAxes": [{
        "ticks": {
            "beginAtZero": true
        },
        "scaleLabel": {
          "display": true,
          "labelString": "Time (sec)"
        }
      }]
    }
  }
}
-->
</canvas>


---
@title[Putting it all together]
# Putting it all together


+++
![comic-about-video-challenges](https://image.ibb.co/eMtG9K/vid_target.jpg)


+++
#### More detailed review


+++
## Python Pipers
@ul
* FFmpeg - latest codecs, best compression methods with the best quality
* Multiprocessing the `ndarray`s - lets us do it really fast
  * How to avoid having to write to hard disk?
* Figuring out how to get the best of both worlds --> Try it out yourselves! You can check your results [here](https://github.com/rsnk96/fast-cv)
@ulend


+++
@title[Results]
<canvas data-chart="bar">
<!-- 
{
 "data": {
  "labels": ["1-Core", "4-VCore", "4-VCore-piped-ffmpeg","4-VCore-piped-ffmpeg-memory-ts"],
  "datasets": [
   {
    "data":[16.03, 6.79, 0, 0],
    "label":"mp4 ","backgroundColor":"rgba(237,101,101,.95)"
   },
   {
    "data":[38.40, 29.16, 28.84, 29.19],
    "label":"mp4 + H264 ","backgroundColor":"rgba(62,153,147,.9)"
   },
   {
    "data":[23.40, 13.68, 13.07, 14.26],
    "label":"mp4 + H264 (ultrafast)","backgroundColor":"rgba(31,50,55,.9)"
   }
  ]
 },
 "options": { 
    "responsive": "true",
    "title": {
      "display": true,
      "text": "Video Processing Speeds for different methods",
      "fontColor": "gray",
      "fontSize": 20
    },
    "scales": {
      "xAxes": [{
        "scaleLabel": {
          "display": true,
          "labelString": "Method"
        }
      }],
      "yAxes": [{
        "scaleLabel": {
          "display": true,
          "labelString": "Time (s)"
        }
      }]
    }
  }
}
-->
</canvas>



+++?image=http://quotesideas.com/wp-content/uploads/2015/10/mMaddc0.jpg


+++

@ul
* Pipe into memory if I/O is the bottleneck and you have fast memory access rates
* No problem in piping into I/O directly if you have an NvME SSD or any other fast I/O device
@ulend


---
## Thank You!