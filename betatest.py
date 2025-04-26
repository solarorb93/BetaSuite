import numpy as np
from pathlib import Path
import os
import subprocess
import math
import sys
import hashlib
import json
import timeit
from multiprocessing import shared_memory
import cv2
import mss
import onnxruntime

import betautils_config
import betautils_model


from betautils_vision import get_cursor_location

cx, cy = get_cursor_location()
print('Cursor is at x: %4d, y: %4d'%( cx, cy ) )

sct = mss.mss()
monitor = {'top':0,'left':0,'width':320,'height':320,'mon':1}
image_original = np.array(sct.grab(monitor))[:,:,:3]

image = image_original.astype( np.float32 )
image -= [ 103.939, 116.779, 123.68 ]

options = onnxruntime.SessionOptions()
options.log_severity_level = 0

session = betautils_model.get_session()

model_outputs = [ s_i.name for s_i in session.get_outputs() ]
model_input_name = session.get_inputs()[0].name

outputs = session.run( model_outputs, {model_input_name: np.expand_dims( image, axis=0) } )

window_name = 'BetaVision'
cv2.startWindowThread()
cv2.namedWindow( window_name, cv2.WINDOW_NORMAL )
cv2.resizeWindow( window_name, 320, 320 )

cv2.imshow( window_name, image_original )
print("Press q or ctrl+c")
while True:
    if cv2.waitKey(1) and 0xFF==ord("q"):
        cv2.destroyAllWindows()
        break
print("Done")
