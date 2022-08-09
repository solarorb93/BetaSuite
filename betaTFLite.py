import tensorflow as tf

converter = tf.lite.TFLiteConverter.from_keras_model('../model/detector_v2_default_checkpoint.onnx' )
tflite_model = converter.convert()
open ("../model/detector_v2_default_checkpoint_tflite.tflite", 'wb').write(tflite_model )
