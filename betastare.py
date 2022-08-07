import cv2
import os
import time
import hashlib

import betaconst

import betautils_config as bu_config
import betautils_hash   as bu_hash
import betautils_model  as bu_model
import betautils_censor as bu_censor

config_dict = bu_config.config_dict_from_config()
input_delete_probability = config_dict['stare']['input_delete_probability']

bu_config.verify_input_delete_probability( input_delete_probability )

censor_hash = bu_hash.get_censor_hash( config_dict )
session = bu_model.get_session( config_dict )

parts_to_blur = bu_config.get_parts_to_blur( config_dict )

images_to_censor = []
images_to_detect = []

to_censor = []
to_detect = []

num_files = 0
for root,d_names,f_names in os.walk(betaconst.picture_path_uncensored):
    num_files += len( f_names )

fidx = 0

for root,d_names,f_names in os.walk(config_dict['stare']['input_dir']):
    censored_folder = root.replace( config_dict['stare']['input_dir'], config_dict['stare']['output_dir'], 1 )
    os.makedirs( censored_folder, exist_ok=True )

    print( "Processing %s"%(root) )

    for fname in f_names:
        fidx += 1
        t0 = time.perf_counter()
        if True:
        #try:
            (stem, suffix ) = os.path.splitext(fname)

            uncensored_path = os.path.join( root, fname )
            image = cv2.imread( uncensored_path )

            if image is not None:
                (img_h,img_w,_) = image.shape
                image_hash = hashlib.md5(image).hexdigest()[16:]

                censored_path = os.path.join( censored_folder, '%s-%s-%s-%s-%.3f%s'%(stem, image_hash, censor_hash, "+".join(map(str,config_dict['net']['picture_sizes'])), betaconst.global_min_prob, suffix))

                t1 = time.perf_counter() 
                if( not os.path.exists( censored_path ) ):
                    all_raw_boxes = []
                    for size in config_dict['net']['picture_sizes']:
                        box_hash_path = '../pic_hashes/%s-%s-%d-%.3f.gz'%(image_hash,betaconst.picture_saved_box_version, size, betaconst.global_min_prob)

                        if( os.path.exists( box_hash_path ) ):
                            all_raw_boxes.append( bu_hash.read_json( box_hash_path ) )
                            use_nn = False

                        else:
                            raw_boxes = bu_model.raw_boxes_for_img( image, size, session, 0 )

                            bu_hash.write_json( raw_boxes, box_hash_path )
                            all_raw_boxes.append( raw_boxes )
                            use_nn = True

                    if config_dict['censor']['debug']:
                        print( all_raw_boxes )

                    t2 = time.perf_counter()
                    boxes = []
                    for raw_boxes in all_raw_boxes:
                        for item in raw_boxes:
                            res = bu_censor.process_raw_box( config_dict, item, img_w, img_h )
                            if res:
                                boxes.append( res )

                    image = bu_censor.censor_img_for_boxes( config_dict, image, boxes )

                    t3 = time.perf_counter()
                    cv2.imwrite(censored_path, image )

                    delete_result = bu_config.delete_file_with_probability( input_delete_probability, uncensored_path, censored_path )
                    t4 = time.perf_counter()

                    print( "--- Processed %d/%d%s (nn %d)    [%.3f %.3f %.3f %.3f: %.3f]: %s"%(fidx, num_files, delete_result, use_nn, t1-t0, t2-t1, t3-t2, t4-t3, t4-t0, fname ) )

                else:
                    print( "--- Skipping  %d/%d (exists)  [%.3f ----- ----- -----: %.3f]: %s"%(fidx, num_files, t1-t0, t1-t0, fname ) )

            else:
                print( "--- Skipping  %d/%d (not img) [----- ----- ----- -----: -----]: %s"%(fidx, num_files, fname ) )
        else:
        #except BaseException as err:
            print( "--- Skipping  %d/%d (failed)  [----- ----- ----- -----: -----]: %s"%(fidx, num_files, fname ) )
            print( f"Error {err=}, {type(err)=}" )
            time.sleep( 1 )
