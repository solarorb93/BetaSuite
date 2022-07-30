###################################################################
#### If you have completed the 'GPU Acceleration' Steps in the 
#### BetaVision install guide, set this to 1, and it will
#### very, very significantly speed up censoring.
#### If you have not, set this to 0.
#### Only BetaStare and BetaTV are supported with gpu_enabled = 0, 
#### BetaVision is only supported with gpu_enabled=1.
gpu_enabled=1

###################################################################
#### Neural Net input size.  This controls how the net views the image.
#### Different values may be best for different photos.
#### 
#### [ 1280 ]: recommended, good performance and speed tradeoff
#### [ 640 ]:  much faster, decent performance when model fills the frame
#### [ 2560 ]: slower, better for collage or big group photos.  
#### 
#### [ 1280, 2560 ]: combine the two, may be safer than either alone
####
#### [ 0 ]: not recommended, uses photos as-is to neural net.
picture_sizes = [ 1280 ] 

##################################################################
#### BetaTV does not run the neural net on every single frame of a
#### video.  Instead, it runs a few times per second, and then 
#### uses those to censor the whole video.  Set the neural net
#### runs per second here.  More means better accuracy, but slower.
#### 5 is a good sweet spot.  You can drop to 3 if 5 is too slow,
#### but you should probably increase the time_safety values
#### in the censoring config if you do.  15 is what I use for
#### best accuracy.
video_censor_fps = 5

##################################################################
#### BetaVision works by capturing uncensored content from one
#### part of your screen and displaying it censored on another
#### part of your screen.  Here, configure what part of the screen
#### holds the uncensored content.  
vision_cap_monitor = 2
vision_cap_top = 646
vision_cap_left = 2560
vision_cap_height = 1370
vision_cap_width = 1440

#### how long a delay should be imposed on the censored content
#### how low this can go depends on how quickly your system
#### can detect and censor content.  
vision_delay = 0.500 #seconds

###################################################################
###### censoring config
###### this section controls what is censored
###### it applies to both BetaFix and BetaVision

### Items to censor
### Put a # in front of a line to turn it off.
items_to_censor = [
    'exposed_anus',
    'exposed_vulva',
    'exposed_breast',
    'exposed_buttocks',
    'covered_vulva',
    'covered_breast',
    'covered_buttocks',
    'face_femme',
    #'exposed_belly',
    #'covered_belly',
    #'exposed_feet',
    #'covered_feet',
    #'exposed_armpits',
    #'exposed_penis',
    #'exposed_chest',
    #'face_masc',
]

# censor style: whether the default censor should be black bars, pixelate, or blur.  Uncomment
# one of the below (by removing the #).
# you can override these per item below in Item Overrides
#default_censor_style = [ 'bar', (0,0,0) ] # second item is the color of the bar, in RGB code 
default_censor_style = [ 'bar', (247,154,192) ] # second item is the color of the bar, in RGB code 
#default_censor_style = [ 'blur', 50 ] # second item is how aggressive a blur.  20 is a reasonable number.  Higher is more blurry.
#default_censor_style = [ 'pixel', 40 ] # second item is the how much to pixelate.  Higher is more censored.  10 means that a 200x400 pixel region is pixelated to 20x40 pixels.

# min_prob: how confident are we that the item is identified before blocking
default_min_prob = 0.60 #0.50 means 50% certainty

# area_safety: do we want to censor a safety region around the identified region
# note that in the overrides below, this can be set independently for width and height
default_area_safety = 0 # i.e., 0.2 means add 20% to width and 20% to height

# time_safety: how long before and after the identification do we want to censor?
default_time_safety = 0.4 #i.e., 0.3 means 0.3 seconds before and 0.3 seconds after

# Item Overrides: to override any of the above defaults for a specific item
item_overrides = {
        #example:
        #face_masc : {'min_prob': 0.40, 'width_area_safety': 0.3, 'height_area_safety': 0.1, 'time_safety': 0.6 },

        'exposed_vulva':  {'width_area_safety': 0.4, 'height_area_safety': 0.4 },
        'exposed_breast': {'width_area_safety': 0.4 },
        'covered_breast': {'width_area_safety': 0.5 },
        'face_femme': {'censor_style': [ 'pixel', 10 ] }
}


###################################################################
#### Miscellaneous

# If you have more than one graphics card and you care which one
# runs the neural net, change this
# You probably don't need to change this
cuda_device_id = 0

# this determines how various censor styles deal with overlap
# You probably don't need to change this
censor_overlap_strategy = {
        'blur': 'single-pass',
        'bar': 'none',
        'pixel': 'single-pass',
        }

# this determines how pixel and blur censors 
# "scale" with image size.  'feature' is recommended
censor_scale_strategy = 'feature' # scales N->1 by min feature dimension, with a 100 base (so a 200x400 feature would be 2N->1)
#censor_scale_strategy = 'image' # scales N->1 by max image dimension, with 1000 base (so a 2000x1200 image would be 2N->1)
#censor_scale_strategy = 'none' # uses N -> 1 reduction

# this determines how much delay is present in BetaVision
# you may need to adjust this for performance reasons
betavision_delay = 0.5 # seconds

# should BetaVision use image interpolation?
# setting this to true may make videos in BetaVision
# smoother, but creates ghosting.
betavision_interpolate = False

### color for the replacement cursor for BetaVision, in RGB
vision_cursor_color = (168,93,253)
