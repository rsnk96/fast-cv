@title[Piping the Parallelism out of Python]
#### Piping the Parallelism out of Python
## Efficient Video Processing

@size[0.5](_R S Nikhil Krishna_)

@size[0.5](_T Lokesh Kumar_)


---
@title[Computer Vision]
# Computer Vision

+++?image=https://d.ibtimes.co.uk/en/full/1469739/vision-age-ultron.jpg

@ul

* @color[white](Vision)
* @fa[times fa-3x white]

@ulend

+++
## Images in Python

* (Show zooming into pixels)
* Commonly used: OpenCV, scikit-image, PIL
* Command:
  `cv2.imread('cool_file_name.jpg')`

* Irrespective of which library you use, the image reading function normally returns a numpy array

+++
## Videos in Python
* First instantiate a video handler with
  ```python
  cap = cv2.VideoCapture('file.mp4')
  ```
- Read frames and handle them as normal images (numpy arrays) with |
  ```python
  ret, frame = cap.read()
  ```

+++
## How Videos are stored

![codecs-containers](http://apress.jensimmons.com/v4/images/ch4/fig4-1.png)


+++
## OpenCV Codecs

@ul

- If OpenCV detects other backends during build, could preferentially select them as the default backend
- On Linux, V4L is given preference over FFmpeg ==> Problems with H.264 (replace arrow with @fa)
- Generally works:
  - 'MJPG' fourcc (codec) with 'avi' extension (container)
  - 'mp4v' fourcc (codec) with 'mp4' extension

@ulend


+++?image=https://lh3.googleusercontent.com/v1u2eM8qNz2YrzC5E76yjA1xAF-FsrCuB7o6JPm5qQNcH-eccUi_KAYcsQdJ7IazoI5bZZ4fXeBty84w66wUzaUL85_g3sMuJqNrbMnVc3RF_B7K6Aic3HbJSsu_gBD-UhkcrCI2

+++?image=http://dzceab466r34n.cloudfront.net/StreamingMedia/ArticleImages/InlineImages/108157-Netflix-HEVC-ORG.png
https://github.com/Netflix/vmaf


+++?image=https://cnet4.cbsistatic.com/img/2018/03/28/f9e54051-4fc0-4431-add8-22c75dd2a0f9/aomedia-av1-roadmap.jpg



---
@title[FFmpeg]
# FFmpeg



+++
## FFmpeg

@ul

* The Cross-Platform Multimedia Swiss-Knife
* Used by VLC. Youtube (controversial), etc
* Efficiently uses your hardware
* For Ubuntu 15.04+, you can just run `sudo apt-get install ffmpeg`

@ulend

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
## Piping FFmpeg into Python


+++
## Trouble in Paradise


---
@title[Parallelism in Python]
# Parallelism in Python

+++
## Let's get some stuff straight first
* Concurrency != Parallelism
* Multithreading - only useful if interfacing IO devices
* For processing already existing files, multitheading is awful, go for multiprocessing

Note:

* Concurrency: Multiple tasks running interleaved
* Parallelism: Multiple tasks running at the same time
* Concurrency - what lets Windows run many applications at the same time

+++
## Python multiprocessing library

@ul

* Circumvents the GIL for CPU ops
* Can allow for data/memory sharing
* CPython only
* Processes are more "heavy-weight", can be slow to start compared to threads

@ulend


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
      out.write(frame)
```



+++
### CV - The multiprocessing way

```python
  def process_video(group_number):
    cap = cv2.VideoCapture("input_file.mp4")
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_jump_unit * group_number)
    proc_frames = 0
    out = cv2.VideoWriter("output_{}.avi".format(group_number), ...)
    while proc_frames < frame_jump_unit:
      ret, frame = cap.read()
      if ret == False:
        break
      out.write(frame)
    out.release()
    return None

  import multiprocessing as mp
  num_processes = mp.cpu_count()
  cap = cv2.VideoCapture("input_file.mp4")
  frame_jump_unit = cap.get(cv2.CAP_PROP_FRAME_COUNT) // num_processes
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

@[14-16](Number of parallel sub-processes)
@[17](Number of frames for each sub-process to process)
@[1-12](We modify the original function a bit)
@[1,3,4](The critical changes)
@[20-21](And now we parallelize the processing of the video)
@[23-28](Merge the videos)


---
@title[Putting it all together]
# The Grand Finale


+++
## Results


+++
## Python Pipers


---?image=http://quotesideas.com/wp-content/uploads/2015/10/mMaddc0.jpg


---
@title[Theme Switcher]

## Slideshow Theme Switcher
<span style="font-size:0.6em; color:gray">Available inside burger-menu.</span> |
<span style="font-size:0.6em; color:gray">Start switching themes right now!</span>

---
@title[Go Fullscreen]

## Tip!
For the *best viewing experience*   
press **F** key to go fullscreen.

---

## Markdown Slides
<span style="font-size:0.6em; color:gray">Press Down key for details.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Slide-Markdown) for details.</span>

@fa[arrow-down]

+++
@title[GFM]

#### Use GitHub Flavored Markdown
#### For Slide Content Creation

<br>

The *same syntax* you use to create project   
**READMEs** and **Wikis** for your Git repos.

---

## Code Presenting
## Repo Source Files
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Code-Presenting) for details.</span>

@fa[arrow-down]

+++?code=src/go/server.go&lang=golang&title=Source: Golang File

@[1,3-6](Present code found within any repo source file.)
@[8-18](Without ever leaving your slideshow.)
@[19-28](Using GitPitch code-presenting with (optional) annotations.)

---
@title[Present Static Block]

## Code Presenting
## Static Source Blocks
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Code-Presenting) for details.</span>

@fa[arrow-down]

+++
<p><span class="menu-title slide-title">Source: JavaScript Block</span></p>

```javascript
// Include http module.
var http = require("http");

// Create the server. Function passed as parameter
// is called on every request made.
http.createServer(function (request, response) {
  // Attach listener on end event.  This event is
  // called when client sent, awaiting response.
  request.on("end", function () {
    // Write headers to the response.
    // HTTP 200 status, Content-Type text/plain.
    response.writeHead(200, {
      'Content-Type': 'text/plain'
    });
    // Send data and end response.
    response.end('Hello HTTP!');
  });

// Listen on the 8080 port.
}).listen(8080);
```

@[1,2](You can present code inlined within your slide markdown too.)
@[9-17](Displayed using code-syntax highlighting just like your IDE.)
@[19-20](Again, all of this without ever leaving your slideshow.)

---
@title[Present GIST]

## Code Presenting
## GitHub GIST
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Code-Presenting) for details.</span>

@fa[arrow-down]

+++?gist=onetapbeyond/494e0fecaf0d6a2aa2acadfb8eb9d6e8&lang=Scala&title=Source: Scala GIST

@[23](You can even present code found within any GitHub GIST.)
@[41-53](GIST source code is beautifully rendered on any slide.)
@[57-62](Code-presenting works seamlessly both online and offline.)

---
@title[Embed Images]

## Image Slides
## [ Inline ]
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Image-Slides) for details.</span>

@fa[arrow-down]

+++

#### Make A Visual Statement

<br>

Use inline images to lend   
a *visual punch* to your slideshow presentations.


+++
@title[Private Investocat]

<span style="color:gray; font-size:0.7em">Inline Image at <b>Absolute URL</b></span>

![Image-Absolute](https://d1z75bzl1vljy2.cloudfront.net/kitchen-sink/octocat-privateinvestocat.jpg)


<span style="color:gray; font-size: 0.5em;">the <b>Private Investocat</b> by [jeejkang](https://github.com/jeejkang)</span>


+++
@title[Octocat De Los Muertos]

<span style="color:gray; font-size:0.7em">Inline Image at GitHub Repo <b>Relative URL</b></span>

![Image-Absolute](assets/octocat-de-los-muertos.jpg)

<span style="color:gray; font-size:0.5em">the <b>Octocat-De-Los-Muertos</b> by [cameronmcefee](https://github.com/cameronmcefee)</span>


+++
@title[Daftpunktocat]

<span style="color:gray; font-size:0.7em"><b>Animated GIFs</b> Work Too!</span>

![Image-Relative](https://d1z75bzl1vljy2.cloudfront.net/kitchen-sink/octocat-daftpunkocat.gif)

<span style="color:gray; font-size:0.5em">the <b>Daftpunktocat-Guy</b> by [jeejkang](https://github.com/jeejkang)</span>

---
@title[Background Images]

## Image Slides
## [ Background ]
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Image-Slides#background) for details.</span>

@fa[arrow-down]

+++
@title[Bold Statements]

#### Make A Bold Visual Statement

<br>

Use high-resolution background images   
for *maximum impact*.

+++?image=https://d1z75bzl1vljy2.cloudfront.net/kitchen-sink/victory.jpg
@title[V For Victory]

+++?image=https://d1z75bzl1vljy2.cloudfront.net/kitchen-sink/127.jpg
@title[127.0.0.1]

---
@title[Embed Video]
## Video Slides
## [ Inline ]
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Video-Slides) for details.</span>

@fa[arrow-down]

+++
@title[YouTube, etc]

#### Bring Your Presentations Alive

<br>

Embed *YouTube*, *Vimeo*, *MP4* and *WebM*   
inline on any slide.

+++
@title[Fresh Guacamole]

![YouTube Video](https://www.youtube.com/embed/dNJdJIwCF_Y)

+++
@title[Gravity]

![Vimeo Video](https://player.vimeo.com/video/125471012)

+++
@title[Big Buck Bunny]

![MP4 Video](http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4)


---
@title[Background Videos]

## Video Slides
## [ Background ]
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Video-Slides#background) for details.</span>

@fa[arrow-down]

+++
@title[Viewer Experience]

#### Maximize The Viewer Experience

<br>

Go fullscreen with *MP4* and *WebM* videos.

+++?video=http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4
@title[Big Buck Bunny]

---

## Math Notation Slides
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Math-Notation-Slides) for details.</span>

@fa[arrow-down]

+++
@title[Beautiful Math]

#### Beautiful Math Rendered Beautifully

<br>

Use *TeX*, *LaTeX* and *MathML* markup   
powered by [MathJax](https://www.mathjax.org).

+++
@title[Sample]

`$$\sum_{i=0}^n i^2 = \frac{(n^2+n)(2n+1)}{6}$$`

+++
@title[Sample]

`\begin{align}
\dot{x} & = \sigma(y-x) \\
\dot{y} & = \rho x - y - xz \\
\dot{z} & = -\beta z + xy
\end{align}`

+++
@title[Sample]

##### The Cauchy-Schwarz Inequality

`\[
\left( \sum_{k=1}^n a_k b_k \right)^{\!\!2} \leq
 \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)
\]`

+++
@title[Inline Sample]

##### In-line Mathematics

This expression `\(\sqrt{3x-1}+(1+x)^2\)` is an example of an inline equation.

---

## Chart Slides
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Chart-Slides) for details.</span>

@fa[arrow-down]

+++
@title[Chart Types]

#### Chart Data Rendered Beautifully

<br>

Use *Bar*, *Line*, *Area*, and *Scatter* charts among many other chart types directly within your markdown, all powered by [Chart.js](http://www.chartjs.org).

+++
@title[Sample Line Chart]

<canvas data-chart="line">
<!--
{
 "data": {
  "labels": ["January"," February"," March"," April"," May"," June"," July"],
  "datasets": [
   {
    "data":[65,59,80,81,56,55,40],
    "label":"My first dataset","backgroundColor":"rgba(20,220,220,.8)"
   },
   {
    "data":[28,48,40,19,86,27,90],
    "label":"My second dataset","backgroundColor":"rgba(220,120,120,.8)"
   }
  ]
 },
 "options": { "responsive": "true" }
}
-->
</canvas>

+++
@title[Sample Bar Chart]

<canvas class="stretch" data-chart="horizontalBar">
<!--
{
 "data" : {
  "labels" : ["Grapefruit", "Orange", "Kiwi",
    "Blackberry", "Banana",
    "Blueberry"],
  "datasets" : [{
    "data": [48, 26, 59, 39, 21, 74],
    "backgroundColor": "#e49436",
    "borderColor": "#e49436"
  }]
  },
  "options": {
    "title": {
      "display": true,
      "text": "The most delicious fruit?",
      "fontColor": "gray",
      "fontSize": 20
    },
    "legend": {
      "display": false
    },
    "scales": {
      "xAxes": [{
        "ticks": {
            "beginAtZero": true,
            "max": 80,
            "stepSize": 10,
            "fontColor": "gray"
        },
        "scaleLabel": {
          "display": true,
          "labelString": "Respondents",
          "fontColor": "gray"
        }
      }],
      "yAxes": [{
        "ticks": {
            "fontColor": "gray"
        }
      }]
    }
  }
}
-->
</canvas>

---

## Slide Fragments
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Fragment-Slides) for details.</span>

@fa[arrow-down]

+++

#### Reveal Slide Concepts Piecemeal
@title[Piecemeal Concepts]

<br>

Step through slide content in sequence   
to *slowly reveal* the bigger picture.

+++
@title[Piecemeal Lists]

- Java
- Groovy |
- Kotlin |
- Scala  |
- The JVM rocks! |

+++
@title[Piecemeal Tables]

<table>
  <tr>
    <th>Firstname</th>
    <th>Lastname</th>
    <th>Age</th>
  </tr>
  <tr>
    <td>Jill</td>
    <td>Smith</td>
    <td>25</td>
  </tr>
  <tr class="fragment">
    <td>Eve</td>
    <td>Jackson</td>
    <td>94</td>
  </tr>
  <tr class="fragment">
    <td>John</td>
    <td>Doe</td>
    <td>43</td>
  </tr>
</table>

---
## <span style="text-transform: none">PITCHME.yaml</span> Settings
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Settings) for details.</span>

@fa[arrow-down]

+++
@title[Custom Look and Feel]

#### Stamp Your Own Look and Feel

<br>

Set a default theme, custom logo, custom css, background image, and preferred code syntax highlighting style.

+++
@title[Custom Behavior]

#### Customize Slideshow Behavior

<br>

Enable auto-slide with custom slide intervals, presentation looping, and RTL flow.


---
@title[Keyboard Controls]
## Slideshow Keyboard Controls
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Fullscreen-Mode) for details.</span>

@fa[arrow-down]

+++
@title[Try Out Now!]

#### Try Out These Great Features Now!

<br>

| Mode | On Key | Off Key |
| ---- | :------: | :--------: |
| Fullscreen | F |  Esc |
| Overview | O |  O |
| Blackout | B |  B |
| Help | ? |  Esc |


---

## GitPitch Social
<span style="font-size:0.6em; color:gray">Press Down key for examples.</span> |
<span style="font-size:0.6em; color:gray">See [GitPitch Wiki](https://github.com/gitpitch/gitpitch/wiki/Slideshow-GitHub-Badge) for details.</span>

@fa[arrow-down]

+++
@title[Designed For Sharing]

#### Slideshows Designed For Sharing

<br>

- View any slideshow at its public URL
- [Promote](https://github.com/gitpitch/gitpitch/wiki/Slideshow-GitHub-Badge) any slideshow using a GitHub badge
- [Embed](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Embedding) any slideshow within a blog or website
- [Share](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Sharing) any slideshow on Twitter, LinkedIn, etc
- [Print](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Printing) any slideshow as a PDF document
- [Download and present](https://github.com/gitpitch/gitpitch/wiki/Slideshow-Offline) any slideshow offline

---
@title[Get The Word Out!]

## GO FOR IT.
## JUST ADD <span style="color:#e49436; text-transform: none">PITCHME.md</span> ;)
