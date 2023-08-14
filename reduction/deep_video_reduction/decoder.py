import joblib
import tensorflow as tf
from imageio import imread
from argparse import ArgumentParser
import numpy as np
import cv2

def load_graph(frozen_graph_filename):
    with tf.io.gfile.GFile(frozen_graph_filename, "rb") as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)
    return graph


def decoder(loadmodel, refer_path, outputfolder):
    graph = load_graph(loadmodel)

    reconframe = graph.get_tensor_by_name('import/build_towers/tower_0/train_net_inference_one_pass/train_net/ReconFrame:0')
    print("reconframe", reconframe)
    print(type(reconframe))

    res_input = graph.get_tensor_by_name('import/quant_feature:0')
    print("res_input", res_input)
    print(type(res_input))

    res_prior_input = graph.get_tensor_by_name('import/quant_z:0')
    print("res_prior_input", res_prior_input)
    print(type(res_prior_input))

    motion_input = graph.get_tensor_by_name('import/quant_mv:0')
    print("motion_input", motion_input)
    print(type(motion_input))

    previousImage = graph.get_tensor_by_name('import/input_image_ref:0')
    print("previousImage", previousImage)
    print(type(previousImage))

    with tf.compat.v1.Session(graph=graph) as sess:

        with open(outputfolder + 'quantized_res_feature.pkl', 'rb') as f:
            residual_feature = joblib.load(f)
        print('residual_feature', residual_feature)
        print(np.unique(residual_feature))

        with open(outputfolder + 'quantized_res_prior_feature.pkl', 'rb') as f:
            residual_prior_feature = joblib.load(f)
        print('residual_prior_feature', residual_prior_feature)
        print(np.unique(residual_prior_feature))

        with open(outputfolder + 'quantized_motion_feature.pkl', 'rb') as f:
            motion_feature = joblib.load(f)
        print('motion_feature', motion_feature)
        print(np.unique(motion_feature))

        im2 = imread(refer_path)
        im2 = im2 / 255.0
        im2 = np.expand_dims(im2, axis=0)

        # reconstructed image
        recon_d = sess.run(
            [reconframe],
            feed_dict={
                res_input: residual_feature,
                res_prior_input: residual_prior_feature,
                motion_input: motion_feature,
                previousImage: im2
            })
        print('recon_d', recon_d)
        reconstructed_image = np.squeeze(recon_d)
        cv2.imwrite(outputfolder + 'output.png', 255*reconstructed_image)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--DecoderModel', type=str, dest="loadmodel", default='./model/L512/frozen_model_D.pb', help="decoder model")
    parser.add_argument('--refer_frame', type=str, dest="refer_path", default='./image/im002.png', help="refer image path")
    parser.add_argument('--loadpath', type=str, dest="outputfolder", default='./testpkl/', help="saved pkl file")

    args = parser.parse_args()
    decoder(**vars(args))
