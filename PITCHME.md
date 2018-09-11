@title[Efficient Video Processing]
#### Piping the Parallelism out of Python
## Efficient Video Processing

@size[0.5](_R S Nikhil Krishna_)
@size[0.5]( @rsnk96 )

---
@transition[fade-out]
@snap[north]
## Why Bother?
@snapend
* 2009: Youtube announces 1080p,      30  fps support
* 2015: Youtube annonces  8k (4320p), 60  fps support
* 2016: AMD     announces 16k (8640p),240 fps support for VR data

<font size="1">AMD announces 16k support: https://www.tweaktown.com/news/53163/amd-radeon-pro-graphics-card-powers-16k-display-15-360-8640/index.html</font>



+++
@transition[fade]
## Why Bother?
`\begin{align}
\small{\text{Demand}} & = \tiny{\frac{(7680 \times 4320) \times 120 \ \text{[2018]} }{(1280 \times 720) \times 60 \ \text{[2009]} }} & = 72\text{x} \\
\small{\text{Supply}} & = \tiny{\frac{3 \ \textrm{TB} \quad \text{[2018]} }{500 \ \textrm{GB} \quad \text{[2009]} }} & = 6\text{x} \\
\tiny{ \text{(HDD Capacityfor 100 USD)}} &  & 
\end{align}`

![shock](https://pa1.narvii.com/6913/8b28b2536160f3d35a3153febcc17ba792d6f28er1-500-271_hq.gif)


+++
### The Problem
![comic-about-video-challenges](https://image.ibb.co/bK5A2z/vid_targets.jpg)


---
@title[Computer Vision]
# Computer Vision


+++?image=https://d.ibtimes.co.uk/en/full/1469739/vision-age-ultron.jpg
@ul
* @fa[desktop white] @color[white](Vision ?)
* @fa[times fa-3x white]
@ulend


+++
## Images
![image-to-pixels](https://media.giphy.com/media/YUxfQeQSLpCU0wT9fA/giphy.gif)


+++
## Images in Python
* Commonly used: OpenCV, scikit-image, PIL
* Reading an image in Python using OpenCV
  ```python
  cv2.imread('cool_file_name.jpg')
  ```
* Standard: Handle images as numpy array


+++
## Videos
@ul
* 28x28 grayscale image @fa[long-arrow-right] 784 bytes
* 1080p Song (300 seconds) @fa[long-arrow-right] `\[ \tiny{\frac{(1080 \times 1920 \times 3) \times (30 \times 300)}{10^9}} ~= \Large{56\ \text{GB}} \]` ![shock](https://girlsarethenewboys.files.wordpress.com/2018/03/what-say-what-dafuq-wtf-what-the-fuck-gif.gif)
@ulend

@transition[none]
@snap[north-east]
<img src="https://media.giphy.com/media/YUxfQeQSLpCU0wT9fA/giphy.gif" width=125 />
@snapend

Note:
* Vid: Flipbook example
* Vid proc not by loading all frames
* To understand, we've to first understand how videos are stored

+++
## Videos
![codecs-containers](http://apress.jensimmons.com/v4/images/ch4/fig4-1.png)

Note:
* For same container, ANY ONE of 10-20 different CODECs can be used
* Codec choice will affect both file size and quality
* The Big Problem: All of those Python computer vision libraries we looked at earlier don't support writing in most codecs. So if you are an industry where you need to, say Analyse Videos and Provide Insights to your customers from the video, then you might be hugely discouraged from using Python in the first place because of this.


+++
## Videos in Python
* First instantiate a video handler with
  ```python
  cap = cv2.VideoCapture('file.mp4')
  ```
* Read frames and handle them as normal images (numpy arrays) with |
  ```python
  ret, frame = cap.read()
  ```

+++?image=https://lh3.googleusercontent.com/v1u2eM8qNz2YrzC5E76yjA1xAF-FsrCuB7o6JPm5qQNcH-eccUi_KAYcsQdJ7IazoI5bZZ4fXeBty84w66wUzaUL85_g3sMuJqNrbMnVc3RF_B7K6Aic3HbJSsu_gBD-UhkcrCI2


+++
## Modern Codecs
<div class="left">
![x265](http://dzceab466r34n.cloudfront.net/StreamingMedia/ArticleImages/InlineImages/108157-Netflix-HEVC-ORG.png)
</div>
<div class="right">
![av1](https://cnet4.cbsistatic.com/img/2018/03/28/f9e54051-4fc0-4431-add8-22c75dd2a0f9/aomedia-av1-roadmap.jpg)
</div>
<font size=1>https://github.com/Netflix/vmaf</font>


---
@title[FFmpeg]
# FFmpeg


+++
## FFmpeg
@ul
* The Cross-Platform Multimedia Swiss-Knife
* Used by VLC, Youtube (controversial), etc
* For Ubuntu 15.04+, you can just run `sudo apt-get install ffmpeg`
@ulend

Note:
* Youtube controversy: FFmpeg has GPL license, so you don't need to openly claim that you use it. contributors to FFmpeg made a bug in the processing pipeline, not a fatal bug. Same bug shows up in FFmpeg too

+++
## Why, though?
* Efficiently uses your hardware
    <div class="left">
    ![normal-cv-htop](https://preview.ibb.co/nCYV2z/normal_cv_htop.png)
    </div>
    <div class="right">
    ![ffmpeg-htop](https://image.ibb.co/kb0zvK/ffmpeg_htop.png)
    </div>
    
* Supports most modern day codecs (BIG win over OpenCV)


+++
## Usage
```
ffmpeg -i  input.avi  output.mp4 
                      cool_output.gif
                      audio_ripper.mp3
                      frame%d.jpg

ffmpeg -codecs
       -formats
```


+++
## Trouble in Paradise
* Adding a filter to ffmpeg is non-trivial
  * Lot of callback functions to define:
    ```python
    init(), uninit(), query_formats(), config_props(), filter_frame()
    ```
  * You have to code in `C`
* What if we want to do more than just adding a filter?

<font size="2">Source: https://github.com/FFmpeg/FFmpeg/blob/master/doc/writing_filters.txt</font>

Note:
* Any industry dealing in just giving clients videos ==>  more than basic filters.
* ffmpeg accessible through terminal only==> pipe the data from numpy to ffmpeg from within Python


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

Read Zulko's blog for more
<font size="2">Source: http://zulko.github.io/blog/2013/09/27/read-and-write-video-frames-in-python-using-ffmpeg/</font>

Note:
* sp is subprocess lib
* What these 3 - 4 lines do: Let you access SotA codecs from within Python


+++?image=https://preview.ibb.co/nBgbee/avi.png

+++?image=https://preview.ibb.co/k7JHkK/h264.png
@transition[none]

---
@title[Parallelism in Video Processing]
# Parallelism in Video Processing


+++
## Let's get some stuff straight first
* Concurrency != Parallelism
* Multithreading - generally useful only when interfacing w/ IO devices
* For processing existing files, multithreading is awful, go for multiprocessing
* Processes are more "heavy-weight", can be slow to start compared to threads

Note:
* FFmpeg speeds up processing by parallelizing the processing of each frame, rather than parallelizing across frames. But parallelizing across frames is a much more fundamental approach, if you think about it, you handle each frame independently.


+++?image=https://media.giphy.com/media/pzAU8uEKFcRAsTjdKQ/giphy.gif
@ul
* @fa[times fa-4x black]
@ulend

Note:
* Video compression is generally inter-frame, so we store some key frames and note how successive frames differ from the previous ones.

+++?image=https://media.giphy.com/media/2lh9grOpTCXnaP3zgw/giphy.gif


+++
### CV - The normal way
```python
  def process_video():
    cap = cv2.VideoCapture("input_file.mp4")
    out = cv2.VideoWriter("output_file.avi", ...)
    while (cap.isOpened()):
      ret, frame = cap.read()
      if ret == False:
        break
      # ... do some stuff ...
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
      if ret == False:
        break
      # ... do some stuff ...
      out.write(frame)
    out.release()
    return None

  import multiprocessing as mp
  num_processes = mp.cpu_count()
  cap = cv2.VideoCapture("input_file.mp4")
  frame_jump = cap.get(cv2.CAP_PROP_FRAME_COUNT) // num_processes
  cap.release()

  p = mp.Pool(num_processes)
  p.map(process_video, range(num_processes))

  intermediate_files = ["output_{}.avi".format(i) for i in range(num_processes)]
  with open("temp_files.txt", "w") as f:
    for t in intermediate_files:
      f.write("file {} \n".format(t))
  ffmpeg_command = "ffmpeg -f concat -safe 0 -i temp_files.txt -vcodec copy"
  sp.Popen(ffmpeg_command, shell=True).wait()
```


@[15-16](Number of parallel sub-processes)
@[18](Number of frames for each sub-process to process)
@[1-13](We modify the original function a bit)
@[1,3-6](The important changes)
@[21-22](And now we parallelize the processing of the video)
@[24-29](Merge the videos)


+++
The `# ... do some stuff ...` :
<table border=0>
  <tr>
    <td>![original-image](https://image.ibb.co/hvGqTK/og.png)</td>
    <td valign="middle">@fa[long-arrow-right]</td>
    <td>![changed-image](https://image.ibb.co/i4wDhe/changed.png)</td>
  </tr>
</table>

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
    "data":[16.03, 6.79],
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
![comic-about-video-challenges](https://image.ibb.co/bK5A2z/vid_targets.jpg)


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