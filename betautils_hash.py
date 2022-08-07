import gzip
import hashlib
import json

import betautils_config as bu_config

import betaconst

def dictionary_hash( to_hash, hash_len ):
    dict_hash = hashlib.md5(json.dumps( to_hash, sort_keys=True, ensure_ascii=True).encode('utf-8')).hexdigest()
    return( dict_hash[:hash_len] )

def get_censor_hash( config_dict ):
    hash_dict = {
            'censor': config_dict['censor'],
            'items':  config_dict['items' ],
            'picture_sizes': config_dict['net']['picture_sizes']
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
