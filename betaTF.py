import onnx
from onnx_tf.backend import prepare

onnx_model = onnx.load( '../model/detector_v2_default_checkpoint.onnx' )
tf_rep = prepare( onnx_model )
tf_rep.export_graph( '../model/detector_v2_default_checkpoint_TF.pb' )
