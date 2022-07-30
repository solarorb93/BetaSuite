import cv2
import numpy as np
import time

import betaconfig

def get_screenshot( sct ):
    monitor = {
            'left': betaconfig.vision_cap_left,
            'top': betaconfig.vision_cap_top,
            'width': betaconfig.vision_cap_width,
            'height': betaconfig.vision_cap_height,
            'mon': betaconfig.vision_cap_monitor,
    }

    sct_time = time.monotonic()
    sct_img = np.array( sct.grab( monitor ) )[:,:,:3]

    return( [ sct_time, sct_img ] )

def shm_name_for_screenshot( size ):
    return( 'raw_grab_%d'%size )

def interpolate_images( img1, ts1, img2, ts2, timestamp ):
    assert( ts1 < ts2 )
    if timestamp < ts1:
        return( img1 )
    if ts2 < timestamp:
        return( img2 )

    pct2 = (timestamp - ts1)/(ts2 - ts1)
    pct1 = 1 - pct2

    return( cv2.addWeighted( img1, pct1, img2, pct2, 0 ) )

def vision_adj_img_size( max_length ):
    if max_length != 0:
        return( ( max_length, max_length ) )
    else:
        return( ( betaconfig.vision_cap_height, betaconfig.vision_cap_width ) )
