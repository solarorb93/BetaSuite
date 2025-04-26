import cv2
import math
import numpy as np
import onnxruntime

import betaconfig
import betaconst
from betautils_config import get_providers


def get_session():
    session = onnxruntime.InferenceSession( '../model/detector_v2_default_checkpoint.onnx', providers=get_providers())
    return( session )

def get_resize_scale( img_h, img_w, max_length ):
    if max_length == 0:
        return(1)
    else:
        return( max_length/max(img_h,img_w) )

def get_image_resize_scale( raw_img, max_length ):
    (s1, s2, _) = raw_img.shape
    return( get_resize_scale( s1, s2, max_length ) )

def prep_img_for_nn( raw_img, size, scale ):
    adj_img = cv2.resize( raw_img, None, fx=scale, fy=scale )

    if size > 0:
        (h,w,_) = adj_img.shape
        adj_img = cv2.copyMakeBorder( adj_img, 0, size - h, 0, size - w, cv2.BORDER_CONSTANT, value=0 )

    adj_img = adj_img.astype(np.float32)
    adj_img -= [103.939, 116.779, 123.68 ]
    return( adj_img )

def get_raw_model_output( img_array, session ):
    output = [
            np.zeros( (len( img_array ), 300, 4 ), dtype = np.float32 ),
            np.zeros( (len( img_array ), 300 ), dtype = np.float32 ),
            np.zeros( (len( img_array ), 300 ), dtype = np.int32 ),
    ]

    for i,img in enumerate( img_array ):
        (output[0][i], output[1][i], output[2][i]) = session.run( betaconst.model_outputs, {betaconst.model_input: [img_array[i]]})

    return( output )

def raw_boxes_from_model_output( model_output, scale_array, t ):
    all_raw_boxes = []
    all_boxes   = model_output[0]
    all_scores  = model_output[1]
    all_classes = model_output[2]
    for boxes, scores, classes, scale in zip( all_boxes, all_scores, all_classes, scale_array ):
        raw_boxes = []
        for box, score, class_id in zip( boxes, scores, classes ):
            if score > betaconst.global_min_prob:
                raw_boxes.append( {
                    'x': float(math.floor(box[0]/scale)),
                    'y': float(math.floor(box[1]/scale)),
                    'w': float(math.ceil((box[2]-box[0])/scale)),
                    'h': float(math.ceil((box[3]-box[1])/scale)),
                    'class_id': float(class_id),
                    'score': float(score),
                    't': t,
                } )
        all_raw_boxes.append(raw_boxes)
    return( all_raw_boxes )

def detect_raw_boxes( img_array, session, scale_array, t ):
    model_output = get_raw_model_output( img_array, session )
    return( raw_boxes_from_model_output( model_output, scale_array, t ) )
    
def raw_boxes_for_img( img, size, session, t ):
    scale = get_image_resize_scale( img, size )
    adj_img = prep_img_for_nn( img, size, scale )
    raw_boxes = detect_raw_boxes( np.expand_dims( adj_img, axis=0 ), session, [ scale ], t )[0]
    return( raw_boxes )

