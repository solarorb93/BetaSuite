import os
import random

import betaconfig
import betaconst

def get_parts_to_blur( config_dict ):
    parts_to_blur={}
    for entry in config_dict[ 'items' ]:
        if entry[ 'enabled' ]:
            parts_to_blur[entry[ 'label' ]] = {
                    'min_prob':           entry[ 'min_prob' ] if entry[ 'is_custom' ] else config_dict['censor']['default_min_prob'],
                    'width_area_safety':  entry[ 'width_area_safety' ] if entry[ 'is_custom' ] else config_dict['censor']['default_area_safety'],
                    'height_area_safety':  entry[ 'height_area_safety' ] if entry[ 'is_custom' ] else config_dict['censor']['default_area_safety'],
                    'time_safety':  entry[ 'time_safety' ] if entry[ 'is_custom' ] else config_dict['censor']['default_time_safety'],
                    'censor_style':  entry[ 'censor_style' ] if entry[ 'is_custom' ] else config_dict['censor']['default_censor_style'],
            }

    if betaconfig.debug_mode&1:
        for item in betaconst.classes:
            parts_to_blur[item[0]] = {
                    'min_prob': betaconst.global_min_prob,
                    'width_area_safety': 0,
                    'height_area_safety': 0,
                    'time_safety': 0.4,
                    'censor_style': [ 'debug', item[1] ]
            }

    return parts_to_blur

def config_dict_from_config():
    config_dict = {
            'censor': {
                'enable': True,
                'debug': True if betaconfig.debug_mode else False,
                'default_censor_style': betaconfig.default_censor_style,
                'default_min_prob': betaconfig.default_min_prob,
                'default_area_safety': betaconfig.default_area_safety,
                'default_time_safety': betaconfig.default_time_safety,
                'enable_betasuite_watermark': betaconfig.enable_betasuite_watermark,
                'censor_scale_strategy': betaconfig.censor_scale_strategy,
                'censor_overlap_strategy': betaconfig.censor_overlap_strategy,
            },
            'net': {
                'gpu_enabled': betaconfig.gpu_enabled,
                'picture_sizes': betaconfig.picture_sizes,
                'cuda_device_id': betaconfig.cuda_device_id,
            },
            'stare': {
                'input_dir': betaconst.picture_path_uncensored,
                'output_dir': betaconst.picture_path_censored,
                'input_delete_probability': betaconfig.input_delete_probability,
            },
            'tv': {
                'input_dir': betaconst.video_path_uncensored,
                'output_dir': betaconst.video_path_censored,
                'input_delete_probability': betaconfig.input_delete_probability,
                'video_censor_fps': betaconfig.video_censor_fps,
            },
            'vision': {
                'vision_cap_monitor': betaconfig.vision_cap_monitor,
                'vision_cap_top': betaconfig.vision_cap_top,
                'vision_cap_left': betaconfig.vision_cap_left,
                'vision_cap_height': betaconfig.vision_cap_height,
                'vision_cap_width': betaconfig.vision_cap_width,
                'vision_cursor_color': betaconfig.vision_cursor_color,
                'vision_delay': betaconfig.betavision_delay,
                'vision_interpolate': betaconfig.betavision_interpolate,
            }
    }

    items = []
    for label in betaconst.label_display_order:
        entry = {}
        entry[ 'label'     ] = label
        entry[ 'enabled'   ] = label in betaconfig.items_to_censor
        entry[ 'is_custom' ] = label in betaconfig.item_overrides

        entry[ 'min_prob'           ] = betaconfig.item_overrides.get( label, {} ).get( 'min_prob',           betaconfig.default_min_prob    )
        entry[ 'width_area_safety'  ] = betaconfig.item_overrides.get( label, {} ).get( 'width_area_safety',  betaconfig.default_area_safety )
        entry[ 'height_area_safety' ] = betaconfig.item_overrides.get( label, {} ).get( 'height_area_safety', betaconfig.default_area_safety )
        entry[ 'time_safety'        ] = betaconfig.item_overrides.get( label, {} ).get( 'time_safety',        betaconfig.default_time_safety )
        entry[ 'censor_style'       ] = betaconfig.item_overrides.get( label, {} ).get( 'censor_style',       betaconfig.default_censor_style )

        items.append( entry )

    config_dict[ 'items' ] = items

    return( config_dict )

def verify_input_delete_probability( prob ):
    if prob == 0:
        return()

    print( '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!' )
    print( 'You have configured BetaSuite to delete input files with a %.2f%% chance.'%(100*prob))
    print( 'If you are SURE this is what you want, enter "DELETE MY FILES" at the prompt' )
    print( 'All upper-case, without the quotes.' )
    print( 'Are you sure?' )
    Res = input()

    if Res == 'DELETE MY FILES':
        print( "Okay!  Proceeding with %.2f%% chance of deleting each input file."%(100*prob) )
        return()
    else:
        print( 'You did not enter "DELETE MY FILES", all upper-case, with no quotes.')
        print( 'Aborting program.' )
        quit()

def delete_file_with_probability( prob, delete_path, check_path ):
    if prob == 0:
        return('')

    if not os.path.exists( check_path ) or os.path.getsize( check_path ) < 1000:
        return( ' (Original NOT DELETED - censored version NOT FOUND)' )

    random_number = random.random()
    if random_number < prob:
        os.remove( delete_path )
        return( ' (Original DELETED!!!!)' )
    else:
        return( ' (Original not deleted)' )
