import hashlib
import json
import betaconfig
import betaconst
import numpy as np
import onnxruntime
import cv2
import math
import subprocess
import gzip

def get_parts_to_blur():
    parts_to_blur={}
    for item in betaconfig.items_to_censor:
        parts_to_blur[item] = {
                'min_prob':           ( betaconfig.item_overrides.get( item, {} ) ).get( 'min_prob',           betaconfig.default_min_prob    ),
                'width_area_safety':  ( betaconfig.item_overrides.get( item, {} ) ).get( 'width_area_safety',  betaconfig.default_area_safety ),
                'height_area_safety': ( betaconfig.item_overrides.get( item, {} ) ).get( 'height_area_safety', betaconfig.default_area_safety ),
                'time_safety':        ( betaconfig.item_overrides.get( item, {} ) ).get( 'time_safety',        betaconfig.default_time_safety ),
                'censor_style':       ( betaconfig.item_overrides.get( item, {} ) ).get( 'censor_style',       betaconfig.default_censor_style ),
        }

    return parts_to_blur

def dictionary_hash( to_hash, hash_len ):
    dict_hash = hashlib.md5(json.dumps( to_hash, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()
    return( dict_hash[:hash_len] )

def get_censor_hash():
    parts_to_blur = get_parts_to_blur()
    hash_dict = {
            'parts_to_blur': parts_to_blur,
            'picture_sizes': betaconfig.picture_sizes,
            'censor_overlap_strategy': betaconfig.censor_overlap_strategy,
            'censor_scale_strategy': betaconfig.censor_scale_strategy,
            }
    ptb_hash = dictionary_hash( hash_dict, betaconst.ptb_hash_len )
    return( ptb_hash )

def write_json( variable, filename ):
    with gzip.open( filename, 'wt', encoding='UTF-8' ) as fout:
        json.dump( variable, fout )

def read_json( filename ):
    with gzip.open( filename, 'rt', encoding='UTF-8' ) as fin:
        return( json.load( fin ) )

def get_session():
    if betaconfig.gpu_enabled:
        providers = [ ( 'CUDAExecutionProvider', { 'device_id': betaconfig.cuda_device_id } ) ]
    else:
        providers = [ ( 'CPUExecutionProvider', {} ) ]

    session = onnxruntime.InferenceSession( '../model/detector_v2_default_checkpoint.onnx', providers=providers )
    return( session )

def get_image_resize_scale( raw_img, max_length ):
    if max_length == 0:
        return(1)
    (s1, s2, _) = raw_img.shape
    scale = max_length/max(s1,s2)
    return( scale )

def prep_img_for_nn( raw_img, size, scale ):
    adj_img = cv2.resize( raw_img, None, fx=scale, fy=scale )

    if size > 0:
        (h,w,_) = adj_img.shape
        adj_img = cv2.copyMakeBorder( adj_img, 0, size - h, 0, size - w, cv2.BORDER_CONSTANT, value=0 )

    adj_img = adj_img.astype(np.float32)
    adj_img -= [103.939, 116.779, 123.68 ]
    return( adj_img )

def detect_raw_boxes( img_array, session, scale_array, t ):
    all_raw_boxes = []
    model_output = session.run( betaconst.model_outputs, {betaconst.model_input: img_array})
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
    
def raw_boxes_for_img( img, size, session, t ):
    scale = get_image_resize_scale( img, size )
    adj_img = prep_img_for_nn( img, size, scale )
    raw_boxes = detect_raw_boxes( np.expand_dims( adj_img, axis=0 ), session, [ scale ], t )[0]
    return( raw_boxes )

def md5_for_file( filename, length ):
    assert length <= 32
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)

    return(file_hash.hexdigest()[32-length:]) 

def censor_scale_for_image_box( image, feature_w, feature_h ):
    if betaconfig.censor_scale_strategy == 'none':
        return(1)
    if betaconfig.censor_scale_strategy == 'feature':
        return( min( feature_w, feature_h ) / 100 )
    if betaconfig.censor_scale_strategy == 'image':
        (img_h,img_w,_) = image.shape
        return( max( img_h, img_w ) / 1000 )

def pixelate_image( image, x, y, w, h, factor ): # factor 10 means 100x100 area becomes 10x10
    factor *= censor_scale_for_image_box( image, w, h )
    new_w = math.ceil(w/factor)
    new_h = math.ceil(h/factor)
    image[y:y+h,x:x+w] = cv2.resize( cv2.resize( image[y:y+h,x:x+w], (new_w, new_h), interpolation = cv2.BORDER_DEFAULT ), (w,h), interpolation = cv2.INTER_NEAREST ) 
    return( image )

def blur_image( image, x, y, w, h, factor ):
    factor = 2*math.ceil( factor * censor_scale_for_image_box( image, w, h )/2 ) + 1
    image[y:y+h,x:x+w] = cv2.blur( image[y:y+h,x:x+w], (factor, factor), cv2.BORDER_DEFAULT )
    #image[y:y+h,x:x+w] = cv2.GaussianBlur( image[y:y+h,x:x+w], (factor, factor), 0 )
    return( image )

def bar_image( image, x, y, w, h, color ):
    image = cv2.rectangle( image, (x,y), (x+w,y+h), color, cv2.FILLED )
    return( image )

def censor_image( image, x, y, w, h, censor_style ):
    if 'blur' == censor_style[0]:
        return( blur_image( image, x,y, w, h, censor_style[1] ) )
    if 'pixel' == censor_style[0]:
        return( pixelate_image( image, x, y, w, h, censor_style[1] ) )
    if 'bar' == censor_style[0]:
        return( bar_image( image, x, y, w, h, censor_style[1] ) )

def process_raw_box( raw, vid_w, vid_h ):
    parts_to_blur = get_parts_to_blur()
    label = betaconst.classes[int(raw['class_id'])]
    if label in parts_to_blur and raw['score'] > parts_to_blur[label]['min_prob']/100:
        x_area_safety = parts_to_blur[label]['width_area_safety']
        y_area_safety = parts_to_blur[label]['height_area_safety']
        time_safety = parts_to_blur[label]['time_safety']
        safe_x = math.floor( max( 0, raw['x'] - raw['w']*x_area_safety/2 ) )
        safe_y = math.floor( max( 0, raw['y'] - raw['h']*y_area_safety/2 ) )
        safe_w = math.ceil( min( vid_w-safe_x, raw['w']*(1+x_area_safety) ) )
        safe_h = math.ceil( min( vid_h-safe_y, raw['h']*(1+y_area_safety) ) )
        return( {
            "start": max( raw['t']-time_safety/2,0 ),
            "end":   raw['t']+time_safety/2,
            "x": safe_x, 
            "y": safe_y, 
            "w": safe_w, 
            "h": safe_h ,
            'censor_style': parts_to_blur[label]['censor_style'],
            'label': label
        } )
    
def rectangles_intersect( box1, box2 ):
    if box1['x']+box1['w'] < box2['x']:
        return( False )

    if box1['y']+box1['h'] < box2['y']:
        return( False )

    if box1['x'] > box2['x']+box2['w']:
        return( False )

    if box1['y'] > box2['y']+box2['h']:
        return( False )

    return( True )

def censor_style_sort( censor_style ):
    if censor_style[0] == 'blur':
        return( 1 + 1/censor_style[1] )
    if censor_style[0] == 'bar':
        return( 2 + 1/(2+255*3-sum(censor_style[1])))
    if censor_style[0] == 'pixel':
        return( 3 + censor_style[1] )
            
def collapse_boxes_for_style( piece ):
    style = piece[0]['censor_style'][0]
    strategy = betaconfig.censor_overlap_strategy[style]
    if strategy == 'none':
        return( piece )
    
    if strategy == 'single-pass':
        segments = []
        for box in piece:
            found = False
            for i,segment in enumerate(segments):
                if rectangles_intersect( box, segment ):
                    x = min( segments[i]['x'], box['x'] )
                    y = min( segments[i]['y'], box['y'] )
                    w = max( segments[i]['x']+segments[i]['w'], box['x']+box['w'] ) - x
                    h = max( segments[i]['y']+segments[i]['h'], box['y']+box['h'] ) - y
                    segments[i]['x']=x
                    segments[i]['y']=y
                    segments[i]['w']=w
                    segments[i]['h']=h
                    found = True
                    break
            if not found:
                segments.append( box )

    return( segments )

def censor_img_for_boxes( image, boxes ):
    boxes.sort( key=lambda x: ( x['label'], censor_style_sort(x['censor_style']) ) )
    pieces = []
    for box in boxes:
        if len( pieces ) and pieces[-1][0]['label'] == box['label'] and pieces[-1][0]['censor_style']==box['censor_style']:
            pieces[-1].append(box)
        else:
            pieces.append([box])

    for piece in pieces:
        collapsed_boxes = collapse_boxes_for_style( piece )
        for collapsed_box in collapsed_boxes:
            image = censor_image( image, collapsed_box['x'], collapsed_box['y'], collapsed_box['w'], collapsed_box['h'], collapsed_box['censor_style'] )

    return( image )

def video_file_has_audio( filepath ):
    command = [ "../ffmpeg/bin/ffprobe.exe",
            '-loglevel', 'error',
            '-show_entries', 'stream=index,codec_type',
            '-of', 'csv=p=0',
            filepath
    ]

    res = subprocess.run( command, capture_output=True )
    decoded = res.stdout.decode()
    if 'audio' in decoded:
        return( True )
    else:
        return( False )
