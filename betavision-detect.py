import numpy as np
import time
from multiprocessing import shared_memory

import betautils
import betaconst
import betaconfig

session = betautils.get_session()

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
    raw_shms.append( shared_memory.SharedMemory( name=betautils.shm_name_for_screenshot( size ) ) )
    raw_screenshots.append( np.ndarray( ( size, size, 3 ), dtype=np.float32, buffer = raw_shms[-1].buf ) )
    local_screenshots.append( np.ndarray( ( size, size, 3 ), dtype=np.float32 ) )

last_timestamp = 0
while( True ):
    start_ts = time.perf_counter()
    # wait for screenshot to be ready
    while( in_timestamp1[0] != in_timestamp2[0] or in_timestamp1[0] == last_timestamp ):
        True

    last_timestamp = in_timestamp1[0]
    for i,local in enumerate(local_screenshots):
        local[:] = raw_screenshots[i][:]

    ( local_out_0, local_out_1, local_out_2 ) = betautils.get_raw_model_output( local_screenshots, session )

    out_timestamp1[0] = last_timestamp
    remote_out_0[:]=local_out_0[:]
    remote_out_1[:]=local_out_1[:]
    remote_out_2[:]=local_out_2[:]
    out_timestamp2[0] = last_timestamp

    print( '%.3f'%(time.perf_counter()-start_ts ) )



    
    
