# BetaSuite

## Welcome to the BetaSuite installation guidelines. 
BetaSuite is composed of the following programs
- BetaTest: this is a test program that tries to ensure, as much as it can, that all of your dependencies are set up correctly.
- BetaStare: this is a program that auto-censors picture files.
- BetaTV: this is a program that auto-censors video files.
- BetaVision: this is a program that performs real-time censoring of your screen.

These are the installation guidelines for BetaSuite v0.2.1.

## Upgrading from previous BetaSuite
If you have not installed BetaSuite before, ignore this section.

If you are upgrading from v0.1.1, you can just redownload BetaSuite, unzip it into InstallFolder/BetaSuite-0.2.1, update betaconfig.py with your settings, and read the section on BetaVision.

If you are upgrading from v0.0.1, you have to do the following steps:
- Delete the ffmpeg you downloaded and download it again.  I'm sorry, I had you download the wrong version.  You need the -gpl version, not the -lgpl version.  You can follow the instructions in the ffmpeg section in this document.
- Create uncensored_vids, censored_vids, and vid_hashes folders in /InstallFolder/, just like you did uncensored_pics, etc.
- Complete the Download BetaSuite section below to download v0.2.1.
- Whatever changes you made to the betaconfig file, make them again in the new betaconfig file
- Read the section on Testing BetaTV to Censor Videos to learn how to use BetaTV, and read the Configuring BetaSuite section to learn about the new config options, and the section on BetaVision to learn to use BetaVision.

## A few quick notes before we begin.

- First, there is no sexual content in these installation guidelines.  I don't know who you are that's reading this, we haven't negotiated any consenting boundaries.  So this is all going to be dry technical material.
- Second, this is not a short or easy process.  BetaSuite is a complex suite of software that has even more complex dependencies.  
- Third, BetaSuite is not magic.  It relies on the v2 NudeNet neural net to identify features to censor and we are extremely grateful to the creators of that net.  In some situations, it will perform better than others.  There is nothing I can really do to make it perform better (aside from training a better neural net, which is far outside my abilities).
- These installation instructions are current as of July 26, 2022.  It is possible that in the future things that BetaSuite depends on may change, and the code may even stop working.
- These instructions are only for Windows.  Many of these things may work under Mac or Linux, but I don't have access to either of them and am not an expert.  Some things almost certainly will not work.
- These files are code that I wrote that runs on your computer.  They are all open-source, and you can read the code before you run it, but if you do not (or cannot) read the code, you are trusting me that these programs will not delete all your data, send your browsing history to your mother, steal your passwords, and use your computer to mine bitcoin.  For what it's worth, I promise that they don't do any of those things.
- During these instructions, anything you have to type will be written `like this`. 

## Installing Basic BetaSuite Dependencies
Yes, you really have to do all these things.  
1. Install Python 3.9
    * BetaSuite is written in Python.  You do not have to be a programmer to use BetaSuite, but you do need to install Python so that the BetaSuite code can run.
    * Right now, Python releases are at https://www.python.org/downloads/windows/.  You must download a version starting with 3.9.  Do not install 3.10 or any other version.  As of this writing, 3.9.13 is the most up to date version of 3.9.  You should install whatever the most up to date version is.
    * When you install Python, make certain that you enable the option to add Python to your PATH variable.
    * To test that python is correctly installed, open a cmd window by going to Start->Run and entering `cmd` and then pressing enter. In the black window that appears, type `python` and then press enter.  You should see a prompt come up that says "Python 3.9" and give you a >>> prompt.  Type `quit()` and press enter to exit.  If you did not get a Python 3.9 prompt, you did not install Python correctly.

2. Install Python Packages
    * BetaSuite relies on a number of public packages for Python that must be installed.
    * Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  Then type the following commands one at a time, hitting enter after each one and allowing the package to install.
        * `pip install mss`
        * `pip install pywin32`
        * `pip install numpy`
        * `pip install opencv-python`
        * `pip install onnxruntime`
    * After each command, you should see Python printing some output.  If any of the output is red text, the package probably did not install correctly and something is wrong.

3. Create BetaSuite directory
    * There needs to be a folder on your computer where all the BetaSuite files will go.  Create a folder somewhere on your computer to hold it.  This location needs to have at least 1GB of free space available,and more if you're censoring very large videos.  It can be anything: C:\BetaSuite\, D:\my_private_folder\censortools\, C:\My Documents\Faxes\Archived\2017\, whatever.  
    * For this entire document, I'll refer to it as InstallFolder.  So if I say to put a file in InstallFolder/model/, that means put the folder in D:\my_private_folder\censortools\model\.  
    * Create the following empty folders in InstallFolder:
        * InstallFolder/uncensored_pics/
        * InstallFolder/censored_pics/
        * InstallFolder/pic_hashes/
        * InstallFolder/uncensored_vids/
        * InstallFolder/censored_vids/
        * InstallFolder/vid_hashes/

4. Install ffmpeg (needed for BetaTV)
    * ffmpeg is used for manipulating video files. Builds for Windows are available here: https://ffmpeg.org/download.html#build-windows .  You may need to hover your mouse over the blue Windows logo on the left hand side to get the Windows links to show up.
    * I recommend clicking on "Windows Builds by BtBN" and then downloading "ffmpeg-master-latest-win64-gpl.zip".  
    * Whatever version you download, unzip it into InstallFolder/ffmpeg/.  So you should have, for example, InstallFolder/ffmpeg/bin/ffmpeg.exe.

5. Download NudeNet neural net model
    * The NudeNet model is the piece of code that identifies features to censor.  It is a single file.  You can download it here: https://github.com/notAI-tech/NudeNet/releases/download/v0/detector_v2_default_checkpoint.onnx
    * If for some reason it is not available at that link, you can download it here: https://mega.nz/file/AjJUETKI#Okdl8LsNHFLh_sx7L-Lb0ls5MyKzJZDky9BHC3kVKrk
    * Download the file and put it in InstallFolder/model/.  So you should have InstallFolder/model/detector_v2_default_checkpoint.onnx.

6. Download BetaSuite
    * Download BetaSuite v0.2.1 source code zip file from this link: https://github.com/solarorb93/BetaSuite/releases/tag/v0.2.1
    * Unzip the files into InstallFolder/BetaSuite-0.2.1/ (so you should have a file InstallFolder/BetaSuite-0.2.1/betastare.py)
    * Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
        * `c:` where c is the letter of the drive that InstallFolder is located on
        * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
        * `python betatest.py`
    * If anything is printed out after the final command, something is incorrect with your setup steps.

## Testing BetaStare to Censor Images
* Take one image you want to censor and copy it to InstallFolder/uncensored_pics
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `c:` where c is the letter of the drive that InstallFolder is located on
    * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
    * `python betastare.py`
* You should now see a censored version of the image in InstallFolder/censored_pics

## Setting up GPU Acceleration
This section is only for users with a modern NVidia graphics card.  If you do not have a modern NVidia graphics card, you will not be able to perform the steps in this section.  If you do have a modern NVidia graphics card, it is *highly* recommended that you do these steps as it will make BetaSuite *much* faster (easily 10x faster, possibly more).
* Hit Ctrl-Shift-Esc to bring up task manager.  Go the Performance Tab, and click on the GPU section on the left-hand panel.  In the top right, you should see something like NVIDIA GeForce GTX 1660 Super.  Generally speaking, if you have a NVIDIA model with a 4-digit model number (1080, 1660, 2080, 3090, etc), you can probably use GPU acceleration.
* For some of the downloads from NVIDIA, you may need to register a developer account on NVIDIA's website.  This is free to do.
* Download CUDA v11.4 from NVIDIA's website.  Right now, CUDA is available here https://developer.nvidia.com/cuda-toolkit-archive .  You can download the latest version of CUDA 11.4 (right now that is 11.4.4).  Install CUDA, following the instructions.
* Download CUDNN.  Right now packages are available at https://developer.nvidia.com/rdp/cudnn-archive .  You must download version 8.2.2 for CUDA 11.4.  The specific package is "cuDNN Library for Windows (x64)".
* Unzip the zip file to InstallFolder/, so you should have a file InstallFolder/cuda/lib/x64/cudnn.lib
* Hit WindowsKey+Pause/Break Key to bring up system settings.  On the right, click on Advanced System Settings.  Then in the window that pops up, click on the Environment Variables button.
* In the window that pops up, in the top half, there is a list of Variables and Values.  There is a variable called Path.  Double-click on Path.  A window will pop up titled "Edit environment variable"
    * Hit the "New" button and enter `InstallFolder/cuda/`, where InstallFolder is your InstallFolder
    * Hit the "New" button and enter `InstallFolder/cuda/bin/`, where InstallFolder is your InstallFolder
    * Hit the "New" button and enter `InstallFolder/cuda/include/`, where InstallFolder is your InstallFolder
    * Hit the "New" button and enter `InstallFolder/cuda/lib/x64/`, where InstallFolder is your InstallFolder
* You should now have added four entries to your Path variable
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `pip uninstall onnxruntime`
    * `pip install onnxruntime-gpu`
* Navigate to InstallFolder/BetaSuite-0.2.1/ and open betaconfig.py in Notepad by right-clicking on it, hovering over "Open With", and choosing Notepad.  In the first section of the file, change gpu_enabled=0 to `gpu_enabled=1`.
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `c:` where c is the letter of the drive that InstallFolder is located on
    * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
    * `python betatest.py`
* If anything is printed out after the final command, something is incorrect with your setup steps.
* If for any reason you cannot make GPU Acceleration work, you need to go back to the original CPU-only setup, by doing the following steps
    * Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
        * `pip uninstall onnxruntime-gpu`
        * `pip install onnxruntime`
    * Navigate to InstallFolder/BetaSuite-0.2.1/ and open betaconfig.py in Notepad by right-clicking on it, hovering over "Open With", and choosing Notepad.  In the first section of the file, change gpu_enabled=1 to `gpu_enabled=0`. Then save and close the file.

## Testing BetaTV to Censor Videos
* Take one video you want to censor and copy it to InstallFolder/uncensored_vids.  I recommend a short video (less than a minute).
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `c:` where c is the letter of the drive that InstallFolder is located on
    * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
    * `python betatv.py` 
* There are three steps that will happen, from slowest to fastest
    * NudeNet detection will run on the video ("processing")
    * The video frames will be censored and encoded to an intermediate format ("encoding")
    * The final video will be re-encoded ("re-encoding")
* You should now see a censored version of the video in InstallFolder/censored_vids

## Testing BetaVision for real-time censoring
BetaVision will almost certainly not work well if you do not have GPU Acceleration enabled.  BetaSuite does not explicitly block it from working, but it will almost surely be unusable.  BetaVision uses a lot of computing power, even with GPU acceleration.

BetaVision uses three scripts to function.  The scripts must be started in the correct order.
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `c:` where c is the letter of the drive that InstallFolder is located on
    * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
    * `python betavision-screenshot.py` which will start the first process.  The program will output numbers that represent how long BetaVision is taking to capture uncensored content, which should usually be under 0.100 (100 milliseconds).
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `c:` where c is the letter of the drive that InstallFolder is located on
    * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
    * `python betavision-detect.py` which will start the second process.  The program will output numbers that represent how long BetaVision is taking to detect features to censor, which should usually be under 0.250 (250 milliseconds).
* Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
    * `c:` where c is the letter of the drive that InstallFolder is located on
    * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
    * `python betavision-censor.py` which will start the third process.  The program will output numbers that represent how long BetaVision is taking to censor the content.  The final number should usualy be under 0.080 (80 milliseconds), and hopefully under 0.050.  
When you run the final command, a window will open that has a copy of the content in the left half of your screen.  If you put censorable content in that part of the screen, it will appear censored in near-real-time (with a 500ms delay, by default).  Sounds will be out-of-sync; a later version of this guide will document how to install VoiceMeeter to sync the sound.
To further configure BetaVision (including what part of the screen is censored), see the Configuring BetaSuite section below.

## Configuring BetaSuite
You can adjust how the censoring works by modifying InstallFolder/BetaSuite-0.2.1/betaconfig.py.  
Navigate to InstallFolder/BetaSuite-0.2.1/ and open betaconfig.py in Notepad by right-clicking on it, hovering over "Open With", and choosing Notepad.
* `gpu_enabled`: this was covered in the "Setting Up GPU Acceleration" section above
* `picture_sizes`: You can experiment with different values to get slightly different censoring.  In general, `[1280]` is recommended, with `[640]` being faster but less accurate and `[2560]` being slower and better for collages or group photos.  You can also combine settings to censor images in multiple passes by having two numbers, like `[1280, 2560]`, which will be slower.  You can also specify `[0]` as a size, which means the full size image or video will be passed to NudeNet.  This is generally not recommended and will usually be slower, but you can experiment with it.
* `video_censor_fps`: for BetaTV, this determines how many frames are run through NudeNet.  Analyzing every frame is very slow.  Instead, BetaTV analyzes a portion of the frames and assumes the features don't move too much between frames.  I use `15`.  All the way down to `5` is reasonable.  Higher number is more accurate, lower number is faster.
* `vision_cap_xxx`: these settings apply to BetaVision and dictate what part of the screen is examined for censoring.  If you have two monitors, I suggest putting the censorable content on the second monitor, and then turning it off, so you can only see the censored version.  An alternative is to put censorable content on the left half of your screen, and cover it with a piece of paper or intentionally not look at it.  You can use the included script betavision-coordinates.py to find the proper numbers for this section.
    * Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
        * `c:` where c is the letter of the drive that InstallFolder is located on
        * `cd InstallFolder/BetaSuite-0.2.1/` where InstallFolder is your InstallFolder
        * `python betavision-coordinates.py` 
    * Put your mouse in the upper-left corner of the region you want to censor.  The window will show the x- and y-coordinates of that spot.  Enter the x coordinate as vision_cap_left and the y-coordinate as vision_cap_top.  Note that these could be negative.
    * Put your mouse in the bottom-right corner of the region you want to censor.  The window will show the x- and y-coordinates of that spot.  Subtract the original coordinates to get the value of vision_cap_width (new x-coordinate minus old x-coordinate) and vision_cap_height (new y-coordinate minus old y-coordinate).
    * You can almost certainly leave vision_cap_monitor as `0`.
* `items_to_censor`: this is a list of what features you want to censor.  Put a `#` before a feature to leave it uncensored.
* `default_censor_style`: This is the censor style that will be used by default on all censored features.  Default censor style is always specified as a list.  The first item in the list is the style; later items are configuring the details of the censoring.  There are three methods supported:
    * `bar`: draws a solid rectangle over the feature.  The second argument is the color of the bar, in RGB.  For example:
        * `default_censor_style = [ 'bar', (0,0,0) ]` draws a black bar
        * `default_censor_style = [ 'bar', (247,154,192) ]` draws a pink bar
    * `blur`: blurs the area.  The second argument is how aggressive the blur is.  A higher number is more blurry.  Note that blur is meaningfully slower than the other methods.  For example:
        * `default_censor_style = [ 'blur', 20 ]` blurs the area
    * `pixel`: pixelates the area.  The second argument is how aggressive the pixelation is.  A higher number is more pixelated.  For example:
        * `default_censor_style = [ 'pixel', 20 ]` pixelates the area
* `default_min_prob`: the neural net assigns a value to how certain it is about identifying a feature.  The default is that the feature is censored if the neural net is more than 60% (`0.6`) sure that the feature is correctly identified, but you can change this up to remove false censors, or move it down to censor more.  You can't decrease this below `0.3`.
* `default_area_safety`: The neural net identifies the area a feature takes up, but you can have the censoring add some padding (to be safer) or shrink the box (to censor slightly less).  `0.2` means add 20% to width and height; `-0.3` means remove 30% from width and height.
* `default_time_safety`: this is relevant for BetaTV and BetaVision.  When NudeNet detects a feature to censor, the censoring is actually extended in time slightly before and slightly after the feature is identified.  This accounts for the fact that we don't analyze every single frame, and for the fact that NudeNet may occasionally miss a feature on a frame.  For example, `default_time_safety = 0.4` means that the censoring extends 0.4 seconds before the feature is found and 0.4 seconds after.  For BetaVision, it is important that this is longer than the time it takes to screenshot and detect, or you will have gaps in coverage.
* `item_overrides`: this allows you to control the above settings on a feature-by-feature basis.  By default, breasts and exposed vulva have increased area safety, based on my testing of the net.
    * Note that you may not get very good results changing the censor style for different features that may overlap.  For example, NudeNet may sometimes identity a nude breast as both a nude breast and a covered breast, so if you have very different censors for the two of them, results may not look great.  In general, I recommend keeping the censor styles the same for features that may be overlapping.  As always, feel free to experiment and see what works best for you.
* `cuda_device_id`: if you have more than one GPU, and want to run BetaSuite GPU Acceleration on a non-primary card, set this.  You probably know what you're doing so I won't tell you how to set it.
* `censor_overlap_strategy`: just leave this as the default, trust me.
* `betavision_delay`: this setting dictates how long content is delayed in BetaVision.  Some delay is necessary, so that censorable content has time to be detected before it is shown to you.  The delay needs to be at least as long as the time it takes your computer to scsreenshot and detect censorable content. 
* `betavision_interpolate`: this setting dictates whether BetaVision will display the last captured frame, or mix the two most recent frames.  Turning this to True makes video smoother, but introduces ghosting and artifacts.  If your system runs too slowly to get smooth video with this set to False, try setting it to True.  Ultimately, this is a personal preference.
* `vision_cursor_color`: BetaVision draws an artificial cursor onto the censored content, so you can see where your mouse is without having to look at the uncensored content.  You can change the color here if you want.
* After you've made changes to betaconfig, save and close the file.  Now you can rerun BetaStare.  BetaStare will re-censor the image with the new settings and place a new copy in InstallFolder/censored_pics/.  
* If this is all working, you are ready to go.  You can copy as many images as you like into InstallFolder/uncensored_pics/ and run BetaStare and as many videos as you like into InstallFolder/uncensored_vids/ and run BetaTV.  Subfolders are supported.  Any files which are not images are skipped (for clarity, animated gifs are not images) in BetaStare and any files which are not videos are skipped in BetaTV.  BetaSuite will be as efficient as possible; if it has already scanned a file with a neural net, it will not do so again (the results are saved in InstallFolder/pic_hashes and vid_hashes).

## Troubleshooting
* If you are having problems getting GPU acceleration to work, especially if you are seeing an error message that includes "Invalid configuration argument", try reinstalling onnxruntime-gpu:
    * Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
        * `pip uninstall onnxruntime-gpu`
        * `pip install onnxruntime-gpu`
* If your program appears "stuck" and is not printing anything in the cmd window, look at the top left of the command window title bar. If it says "Select", then click on the cmd window and press the Escape key.
    * This is a 'feature' in newer versions of Windows.  When you click on a cmd window, it freezes whatever programs are running to allow you to copy text out of the window.  Pressing Escape exits this mode, allowing programs to keep running.
* If you see a error message saying "OpenCV... .... ... The function is not implemented.... .... .." when running BetaVision, try the following:
    * Open a cmd window by going to Start->Run and entering `cmd` and then pressing enter.  In the black window that appears, type the following commands, pressing enter after each one:
        * `pip uninstall opencv-python`
        * `pip install opencv-python`

## Changelog
* v0.2.1: 2022-07-29
    * Introduce BetaVision
    * Change colors to RGB instead of BGR
    * Documentation updates
* v0.1.1: 2022-07-27
    * Don't try to process frames past the last frame of a video
* v0.1.1-rc3: 2022-07-27
    * Handle non-1 audio stream id
    * handle non-even video dimension
    * add troubleshooting section to readme
    * compress hashes to save space
* v0.1.1-rc2: 2022-07-27
    * Move audio to second encoding pass in betatv
* v0.1.1-rc1: 2022-07-26
    * Add BetaTV
    * Add pixel and blur censor methods
    * Add color configuration for bar censoring
    * Add censor_scale_strategy
    * Add censor_overlap_strategy
    * Add some better error handling for BetaStare
* v0.0.1: 2022-07-21
    * Initial Release
