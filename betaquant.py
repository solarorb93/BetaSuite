from onnxruntime.quantization import quantize_static, CalibrationDataReader, QuantType
import betautils_model as bu_model
import os
import cv2
import numpy as np

def preprocess_func(images_folder):
    image_names = os.listdir(images_folder)
    batch_filenames = image_names
    unconcatenated_batch_data = []

    for i,image_name in enumerate(batch_filenames):
        if i == 500: 
            break
        if i%10 == 0:
            print( 'Preprocessing %d'%i )
        image_filepath = images_folder + '/' + image_name
        image_data = cv2.imread( image_filepath )
        image_data = bu_model.prep_img_for_nn( image_data, 640, bu_model.get_image_resize_scale( image_data, 640 ) )
        unconcatenated_batch_data.append(image_data)
    #batch_data = np.concatenate(np.expand_dims(unconcatenated_batch_data, axis=0), axis=0)
    return unconcatenated_batch_data

class MobilenetDataReader(CalibrationDataReader):
    def __init__(self, calibration_image_folder):
        self.image_folder = calibration_image_folder
        self.preprocess_flag = True
        self.enum_data_dicts = []
        self.datasize = 0
        self.i = 0

    def get_next(self):
        if self.preprocess_flag:
            self.preprocess_flag = False
            nhwc_data_list = preprocess_func(self.image_folder)
            self.datasize = len(nhwc_data_list)
            self.enum_data_dicts = iter([{'input_1:0': [nhwc_data]} for nhwc_data in nhwc_data_list])

        self.i = self.i + 1
        print( self.i )

        return next(self.enum_data_dicts, None)

calibration_data_folder = "E:/stuff/organized/censor/nudenet/training-data/DETECTOR_AUTO_GENERATED_DATA/IMAGES_FULL/"

dr = MobilenetDataReader( calibration_data_folder )

quantize_static( '../model/detector_v2_default_checkpoint.onnx', '../model/detect_v2_default_checkpoint_static_640.onnx', dr )

