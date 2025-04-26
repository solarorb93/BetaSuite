import cv2
import math
import numpy as np

import betautils_config as bu_config

import betaconst
import betaconfig

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
    color = tuple( reversed( color ) )
    image = np.ascontiguousarray( image )
    image = cv2.rectangle( image, (x,y), (x+w,y+h), color, cv2.FILLED )
    return( image )

def debug_image( image, box ):
    x = box['x']
    y = box['y']
    w = box['w']
    h = box['h']
    color = tuple( reversed( box['censor_style'][1] ) )
    image = np.ascontiguousarray( image )
    image = cv2.rectangle( image, (x,y), (x+w,y+h), color, 3 )
    image = cv2.putText( image, '(%d,%d)'%(x,y),     (x+10,y+20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1 )
    image = cv2.putText( image, '(%d,%d)'%(x+w,y+h), (x+10,y+40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1 )
    image = cv2.putText( image, box['label'],        (x+10,y+60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1 )
    image = cv2.putText( image, '%.2f %.1f %.1f'%(box['score'],box['start'],box['end'] ), (x+10, y+80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1 )
    return( image )

def censor_image( image, box ):
    if 'blur' == box['censor_style'][0]:
        return( blur_image( image, box['x'], box['y'], box['w'], box['h'], box['censor_style'][1] ) )
    if 'pixel' == box['censor_style'][0]:
        return( pixelate_image( image, box['x'], box['y'], box['w'], box['h'], box['censor_style'][1] ) )
    if 'bar' == box['censor_style'][0]:
        return( bar_image( image, box['x'], box['y'], box['w'], box['h'], box['censor_style'][1] ) )
    if 'debug' == box['censor_style'][0]:
        return( debug_image( image, box ) )

def watermark_image( image ):
    if betaconfig.enable_betasuite_watermark:
        image = np.ascontiguousarray( image )
        (h,w,_) = image.shape
        scale = max( min(w/750,h/750), 1 )
        return( cv2.putText( image, 'Censored with github.com/anatoidea/BetaSuite', (20,math.ceil(20*scale)), cv2.FONT_HERSHEY_PLAIN, scale, (0,0,255), math.floor(scale) ) )
    else:
        return( image )

def annotate_image_shape( image ):
    image = np.ascontiguousarray( image )
    return( cv2.putText( image, str( image.shape ), (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2 ) )

def process_raw_box( raw, vid_w, vid_h ):
    parts_to_blur = bu_config.get_parts_to_blur()
    label = betaconst.classes[int(raw['class_id'])][0]
    if label in parts_to_blur and raw['score'] > parts_to_blur[label]['min_prob']:
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
            'label': label,
            'score': raw['score'],
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
    if censor_style[0] == 'debug':
        return( 99 )
            
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
            image = censor_image( image, collapsed_box )

    image = watermark_image( image )

    return( image )

