import mss
from multiprocessing import Process, Queue, shared_memory
import time
import cv2
import numpy as np
import win32gui, win32ui

import betaconst

import betautils_config as bu_config
import betautils_model as bu_model
import betautils_vision as bu_vision
import betautils_censor as bu_censor

config_dict = bu_config.config_dict_from_config()

### set up for detection
outputs_0_shm = shared_memory.SharedMemory( name=betaconst.bv_detect_shm_0_name )
outputs_1_shm = shared_memory.SharedMemory( name=betaconst.bv_detect_shm_1_name )
outputs_2_shm = shared_memory.SharedMemory( name=betaconst.bv_detect_shm_2_name )

remote_out_0 = np.ndarray( ( len( config_dict['net']['picture_sizes'] ), 300, 4 ), dtype = np.float32, buffer = outputs_0_shm.buf )
remote_out_1 = np.ndarray( ( len( config_dict['net']['picture_sizes'] ), 300 ), dtype = np.float32, buffer = outputs_1_shm.buf )
remote_out_2 = np.ndarray( ( len( config_dict['net']['picture_sizes'] ), 300 ), dtype = np.int32, buffer = outputs_2_shm.buf )

local_out_0 = np.ndarray( remote_out_0.shape, dtype=remote_out_0.dtype )
local_out_1 = np.ndarray( remote_out_1.shape, dtype=remote_out_1.dtype )
local_out_2 = np.ndarray( remote_out_2.shape, dtype=remote_out_2.dtype )

out_timestamp1_shm = shared_memory.SharedMemory( name=betaconst.bv_detect_timestamp1_name )
out_timestamp2_shm = shared_memory.SharedMemory( name=betaconst.bv_detect_timestamp2_name )

remote_timestamp1 = np.ndarray( (1,), dtype=np.float64, buffer = out_timestamp1_shm.buf )
remote_timestamp2 = np.ndarray( (1,), dtype=np.float64, buffer = out_timestamp2_shm.buf )

last_detect_timestamp = 0

scale_array = []
for size in config_dict['net']['picture_sizes']:
    scale_array.append( bu_model.get_resize_scale( config_dict['vision']['vision_cap_width'], config_dict['vision']['vision_cap_height'], size ) )

### set up for censoring
img_buffer = []
boxes = []
window_name = 'BetaVision'
cv2.startWindowThread()
cv2.namedWindow( window_name, cv2.WINDOW_NORMAL )
cv2.resizeWindow( window_name, config_dict['vision']['vision_cap_width'], config_dict['vision']['vision_cap_height'] )
sct = mss.mss()

while( True ):
    times = []
    times.append(time.perf_counter())
    img_buffer.append( bu_vision.get_screenshot( config_dict, sct ) )

    #fixme
    if False:
        cv2.imwrite( 'debug-vision-precensor.png', img_buffer[-1][1] )

    times.append(time.perf_counter())
    if( remote_timestamp1[0] == remote_timestamp2[0] and remote_timestamp1[0] != last_detect_timestamp ):
        last_detect_timestamp = remote_timestamp1[0]
        local_out_0[:]=remote_out_0[:]
        local_out_1[:]=remote_out_1[:]
        local_out_2[:]=remote_out_2[:]

        all_raw_boxes =  bu_model.raw_boxes_from_model_output( [ local_out_0, local_out_1, local_out_2 ], scale_array, last_detect_timestamp )

        raw_boxes = [ box for raw_boxes in all_raw_boxes for box in raw_boxes ]
        this_boxes = [ bu_censor.process_raw_box( config_dict, raw, config_dict['vision']['vision_cap_width'], config_dict['vision']['vision_cap_height'] ) for raw in raw_boxes ]
        this_boxes = [ box for box in this_boxes if box ]
        boxes.extend( this_boxes )
        boxes.sort( key=lambda x: x['end'] )

    times.append(time.perf_counter())
    while( len( boxes ) and boxes[0]['end'] < time.monotonic() - config_dict['vision']['vision_delay'] ):
        boxes.pop(0)

    times.append(time.perf_counter())
    while( len( img_buffer ) > 1 and time.monotonic() - img_buffer[1][0] > config_dict['vision']['vision_delay'] ):
        img_buffer.pop(0)

    times.append(time.perf_counter())
    frame_timestamp = time.monotonic() - config_dict['vision']['vision_delay']

    # nothing in the buffer is old enough
    if img_buffer[0][0] > frame_timestamp:
        continue

    times.append(time.perf_counter())
    if config_dict['vision']['vision_interpolate']:
        frame = bu_vision.interpolate_images( img_buffer[0][1], img_buffer[0][0], img_buffer[1][1], img_buffer[1][0], frame_timestamp )
    else: 
        frame = img_buffer[0][1]

    times.append(time.perf_counter())
    live_boxes = [ box for box in boxes if box['start'] < frame_timestamp < box['end'] ]

    times.append(time.perf_counter())
    frame = bu_censor.censor_img_for_boxes( config_dict, frame, live_boxes )

    if config_dict['censor']['debug']:
        frame = bu_censor.annotate_image_shape( frame )

    flags, hcursor, (cx,cy) = win32gui.GetCursorInfo()
    cx = cx - config_dict['vision']['vision_cap_left']
    cy = cy - config_dict['vision']['vision_cap_top' ]

    if 5<cx<config_dict['vision']['vision_cap_width'] and 5<cy<config_dict['vision']['vision_cap_height']:
        color = tuple(reversed( config_dict['vision']['vision_cursor_color'] ) )
        frame[cy-5:cy+5,cx-5:cx+5] = color
        if config_dict['censor']['debug']&1:
            frame = cv2.putText( frame, '(%d,%d)'%(cx,cy), (max(cx-10,0),max(cy-10,0)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2 )

    #fixme
    if False:
        cv2.imwrite( 'debug-vision-postcensor.png', frame )

    times.append(time.perf_counter())
    cv2.imshow( window_name, frame )
    times.append(time.perf_counter())
    times_display = [ '%.3f'%(x-times[0]) for x in times ]
    print( times_display )

    if cv2.waitKey(1) & 0xFF==ord("q"):
        cv2.destroyAllWindows()
        break
