import mss
import numpy as np
import time
from multiprocessing import shared_memory

import betaconfig

with mss.mss() as sct:
    monitor = {
            'left': betaconfig.vision_cap_left,
            'top': betaconfig.vision_cap_top,
            'width': betaconfig.vision_cap_width,
            'height': betaconfig.vision_cap_height,
            'mon': betaconfig.vision_cap_monitor,
    }

    shared_mem_inited = False

    while( True ):
        sct_time = time.monotonic_ns()
