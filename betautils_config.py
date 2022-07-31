import betaconfig
import betaconst

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

