global_min_prob = 0.30
picture_saved_box_version = 1

ptb_hash_len = 4

model_outputs = [
        'filtered_detections/map/TensorArrayStack/TensorArrayGatherV3:0',   # boxes
        'filtered_detections/map/TensorArrayStack_1/TensorArrayGatherV3:0', # scores
        'filtered_detections/map/TensorArrayStack_2/TensorArrayGatherV3:0', # classes
]

model_input = 'input_1:0'

picture_path_uncensored = '../uncensored_pics/'
picture_path_censored   = '../censored_pics/'

video_path_uncensored = '../uncensored_vids/'
video_path_censored   = '../censored_vids/'

classes = [
    'exposed_anus',
    'exposed_armpits',
    'covered_belly',
    'exposed_belly',
    'covered_buttocks',
    'exposed_buttocks',
    'face_femme',
    'face_masc',
    'covered_feet',
    'exposed_feet',
    'covered_breast',
    'exposed_breast',
    'covered_vulva',
    'exposed_vulva',
    'exposed_chest',
    'exposed_penis',
]

bv_ss_timestamp1_name = 'bv_ss_timestamp1_name'
bv_ss_timestamp2_name = 'bv_ss_timestamp2_name'
bv_detect_timestamp1_name = 'bv_detect_timestamp1_name'
bv_detect_timestamp2_name = 'bv_detects_timestamp2_name'

bv_detect_shm_0_name = "bv_detect_shm_0_name"
bv_detect_shm_1_name = "bv_detect_shm_1_name"
bv_detect_shm_2_name = "bv_detect_shm_2_name"
