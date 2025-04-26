import cv2
import numpy as np
import time
import os

import betaconfig


if os.name == "nt":
    import win32gui
    def get_cursor_location():
        flags, hcursor, (cx,cy) = win32gui.GetCursorInfo()
        return cx, cy
else:
    from Xlib import display
    def get_cursor_location():
        cursor_data = display.Display().screen().root.query_pointer()._data
        cx, cy = cursor_data["root_x"], cursor_data["root_y"]
        return cx, cy


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
