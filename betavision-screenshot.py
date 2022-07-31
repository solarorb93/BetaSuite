import cv2
import mss
import numpy as np
import time
from multiprocessing import shared_memory

import betaconfig
import betaconst

import betautils_model as bu_model
import betautils_vision as bu_vision

with mss.mss() as sct:
    shared_mem_inited = False

    # good enough
    adj_images = []
    shared_images = []
    shms = []
    for _ in betaconfig.picture_sizes:
        adj_images.append( None )

    while( True ):
        ( sct_time, grab ) = bu_vision.get_screenshot( sct )
        timestamp = np.array( [ sct_time ] )

        for i, size in enumerate( betaconfig.picture_sizes ):
            adj_images[i] = bu_model.prep_img_for_nn( grab, size, bu_model.get_image_resize_scale( grab, size ) )

        if not shared_mem_inited:
            for i, size in enumerate( betaconfig.picture_sizes ):
                name = bu_vision.shm_name_for_screenshot( size )
                shm = shared_memory.SharedMemory( name=name, create=True, size=adj_images[i].nbytes )
                shms.append( shm )
                shared_images.append(np.ndarray( adj_images[i].shape, dtype=adj_images[i].dtype, buffer=shms[i].buf ) )
            timestamp1_shm = shared_memory.SharedMemory( name=betaconst.bv_ss_timestamp1_name, create=True, size=timestamp.nbytes )
            timestamp2_shm = shared_memory.SharedMemory( name=betaconst.bv_ss_timestamp2_name, create=True, size=timestamp.nbytes )
            shared_timestamp1 = np.ndarray( timestamp.shape, dtype=timestamp.dtype, buffer=timestamp1_shm.buf )
            shared_timestamp2 = np.ndarray( timestamp.shape, dtype=timestamp.dtype, buffer=timestamp2_shm.buf )
            shared_mem_inited = True

        shared_timestamp1[:]=timestamp[:]
        for i,adj_image in enumerate(adj_images):
            shared_images[i][:]=adj_image[:]
        shared_timestamp2[:]=timestamp[:]

        if betaconfig.debug_mode&2:
            cv2.imwrite( 'debug-vision-raw-screenshot.png', bu_censor.annotate_image_shape( grab ) )
            for i,size in enumerate(betaconfig.picture_sizes):
                cv2.imwrite( 'debug-vision-adj-screenshot-%d-%d.png'%(i,size), bu_censor.annotate_image_shape( adj_images[i] ) )

        print( '%.3f'%(time.monotonic()-sct_time ))

