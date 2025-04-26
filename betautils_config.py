import os
import random
import onnxruntime

import betaconfig
import betaconst


def get_providers():
    """Get provider. Best guess if not specified"""
    if betaconfig.providers is not None:
        return betaconfig.providers
    available = onnxruntime.get_available_providers()
    if "CUDAExecutionProvider" in available:
        return [ ( 'CUDAExecutionProvider', { 'device_id':0 } ) ]  # CUDA GPU for NVIDIA cards
    elif "ROCMExecutionProvider" in available:
        return ["ROCMExecutionProvider", 'CPUExecutionProvider']  # AMD ROCm with CPU fallback
    else:
        return [ ( 'CPUExecutionProvider', {} ) ]  # CPU only


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

    if betaconfig.debug_mode&1:
        for item in betaconst.classes:
            parts_to_blur[item[0]] = {
                    'min_prob': 0.5,
                    'width_area_safety': 0,
                    'height_area_safety': 0,
                    'time_safety': 0.4,
                    'censor_style': [ 'debug', item[1] ]
            }

    return parts_to_blur

def verify_input_delete_probability():
    prob = betaconfig.input_delete_probability
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

def delete_file_with_probability( delete_path, check_path ):
    prob = betaconfig.input_delete_probability
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
