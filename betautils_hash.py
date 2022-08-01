import gzip
import hashlib
import json

import betautils_config as bu_config

import betaconst
import betaconfig

def dictionary_hash( to_hash, hash_len ):
    dict_hash = hashlib.md5(json.dumps( to_hash, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()
    return( dict_hash[:hash_len] )

def get_censor_hash():
    parts_to_blur = bu_config.get_parts_to_blur()
    hash_dict = {
            'parts_to_blur': parts_to_blur,
            'picture_sizes': betaconfig.picture_sizes,
            'censor_overlap_strategy': betaconfig.censor_overlap_strategy,
            'censor_scale_strategy': betaconfig.censor_scale_strategy,
            'enable_betasuite_watermark': betaconfig.enable_betasuite_watermark,
            }
    ptb_hash = dictionary_hash( hash_dict, betaconst.ptb_hash_len )
    return( ptb_hash )

def write_json( variable, filename ):
    with gzip.open( filename, 'wt', encoding='UTF-8' ) as fout:
        json.dump( variable, fout )

def read_json( filename ):
    with gzip.open( filename, 'rt', encoding='UTF-8' ) as fin:
        return( json.load( fin ) )

def md5_for_file( filename, length ):
    assert length <= 32
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)

    return(file_hash.hexdigest()[32-length:]) 
