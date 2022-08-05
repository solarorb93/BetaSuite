import hashlib
import numpy as np
import time
from multiprocessing import shared_memory

import betaconst
import betaconfig

import betautils_vision as bu_vision
import betautils_model as bu_model

session = bu_model.get_session()

in_timestamp1_shm = shared_memory.SharedMemory( name=betaconst.bv_ss_timestamp1_name )
in_timestamp2_shm = shared_memory.SharedMemory( name=betaconst.bv_ss_timestamp2_name )

in_timestamp1 = np.ndarray( (1,), dtype=np.float64, buffer = in_timestamp1_shm.buf ) 
in_timestamp2 = np.ndarray( (1,), dtype=np.float64, buffer = in_timestamp2_shm.buf ) 

out_shm_timestamp1 = shared_memory.SharedMemory( name=betaconst.bv_detect_timestamp1_name, create=True, size=in_timestamp1.nbytes )
out_shm_timestamp2 = shared_memory.SharedMemory( name=betaconst.bv_detect_timestamp2_name, create=True, size=in_timestamp1.nbytes )

out_timestamp1 = np.ndarray( (1,), dtype=np.float64, buffer = out_shm_timestamp1.buf )
out_timestamp2 = np.ndarray( (1,), dtype=np.float64, buffer = out_shm_timestamp2.buf )

local_out_0 = np.ndarray( ( len( betaconfig.picture_sizes ), 300, 4 ), dtype=np.float32 )
local_out_1 = np.ndarray( ( len( betaconfig.picture_sizes ), 300 ), dtype=np.float32 )
local_out_2 = np.ndarray( ( len( betaconfig.picture_sizes ), 300 ), dtype=np.int32 )

out_shm_0 = shared_memory.SharedMemory( name=betaconst.bv_detect_shm_0_name, create=True, size=local_out_0.nbytes )
out_shm_1 = shared_memory.SharedMemory( name=betaconst.bv_detect_shm_1_name, create=True, size=local_out_1.nbytes )
out_shm_2 = shared_memory.SharedMemory( name=betaconst.bv_detect_shm_2_name, create=True, size=local_out_2.nbytes )

remote_out_0 = np.ndarray( local_out_0.shape, local_out_0.dtype, buffer = out_shm_0.buf )
remote_out_1 = np.ndarray( local_out_1.shape, local_out_1.dtype, buffer = out_shm_1.buf )
remote_out_2 = np.ndarray( local_out_2.shape, local_out_2.dtype, buffer = out_shm_2.buf )

raw_shms = []
raw_screenshots = []
local_screenshots = []
for size in betaconfig.picture_sizes:
    raw_shms.append( shared_memory.SharedMemory( name=bu_vision.shm_name_for_screenshot( size ) ) )
    (this_height, this_width) = bu_vision.vision_adj_img_size( size )
    raw_screenshots.append( np.ndarray( ( this_height, this_width, 3 ), dtype=np.float32, buffer = raw_shms[-1].buf ) )
    local_screenshots.append( np.ndarray( ( this_height, this_width, 3 ), dtype=np.float32 ) )

last_timestamp = 0
image_sum = 0
image_hash = 0
while( True ):
    times = [ time.perf_counter() ]
    # wait for screenshot to be ready
    while( in_timestamp1[0] != in_timestamp2[0] or in_timestamp1[0] == last_timestamp ):
        True

    times.append( time.perf_counter() )

    last_timestamp = in_timestamp1[0]
    for i,local in enumerate(local_screenshots):
        local[:] = raw_screenshots[i][:]

    times.append( time.perf_counter() )

    ### we don't want to censor again if image is unchanged
    ### hashing at size 1280 takes 30ms, which is not nothing
    ### summing takes 10ms, which is a lot less overhead.
    ### so start with a very fast check (just sum the image)
    ### if the sum is unchanged, proceed to hash
    ### this means we will Detect the same image twice in a
    ### row, but not more than twice
    new_sum = np.sum( local_screenshots[0] )
    times.append( time.perf_counter() )

    if new_sum == image_sum:
        new_hash = hashlib.md5( local_screenshots[0].tobytes() ).digest()
    else:
        new_hash = 0

    times.append( time.perf_counter() )

    if new_sum != image_sum or new_hash != image_hash:
        ( local_out_0, local_out_1, local_out_2 ) = bu_model.get_raw_model_output( local_screenshots, session )

    times.append( time.perf_counter() )

    image_sum = new_sum
    image_hash = new_hash

    out_timestamp1[0] = last_timestamp
    remote_out_0[:]=local_out_0[:]
    remote_out_1[:]=local_out_1[:]
    remote_out_2[:]=local_out_2[:]
    out_timestamp2[0] = last_timestamp

    times.append( time.perf_counter() )
    print( [ '%.3f'%(x-times[0]) for x in times ] )



    
    
