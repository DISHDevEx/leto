import joblib
import os
import tensorflow as tf
from imageio import imread
import numpy as np
from argparse import ArgumentParser

# Enable eager execution
tf.config.experimental_run_functions_eagerly(True)

def load_graph(frozen_graph_filename):
    with tf.io.gfile.GFile(frozen_graph_filename, "rb") as f: # GFile is tensorflow's file reader. Similar to I/O objects.
        graph_def = tf.compat.v1.GraphDef() # tf.compat.v1.GraphDef A protobuf containing the graph of operations.
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)
    return graph


def encoder(loadmodel, input_path, refer_path, outputfolder):
    graph = load_graph(loadmodel)
    print('---------------------------')
    print("graph",graph)
    print("type", type(graph))
    prefix = 'import/build_towers/tower_0/train_net_inference_one_pass/train_net/'

    Res = graph.get_tensor_by_name(prefix + 'Residual_Feature:0')
    print("Res",Res)
    print("type", type(Res))
    print("shape", Res.shape)
    # print(np.unique(Res))

    inputImage = graph.get_tensor_by_name('import/input_image:0')
    print("inputImage",inputImage)
    print("type", type(inputImage))
    print("shape",inputImage.shape)
    # print(np.unique(inputImage))

    previousImage = graph.get_tensor_by_name('import/input_image_ref:0')
    print("previousImage",previousImage)
    print("type", type(previousImage))
    print("shape",previousImage.shape)
    # print(np.unique(previousImage))

    Res_prior = graph.get_tensor_by_name(prefix + 'Residual_Prior_Feature:0')
    print("Res_prior",Res_prior)
    print("type", type(Res_prior))
    print("shape",Res_prior.shape)
    # print(np.unique(Res_prior))

    motion = graph.get_tensor_by_name(prefix + 'Motion_Feature:0')
    print("motion",motion)
    print("type", type(motion))
    print("shape",motion.shape)
    # print(np.unique(motion))

    bpp = graph.get_tensor_by_name(prefix + 'rate/Estimated_Bpp:0')
    print("bpp",bpp)
    print("type", type(bpp))
    print("shape",bpp.shape)
    # print(np.unique(bpp))

    psnr = graph.get_tensor_by_name(prefix + 'distortion/PSNR:0')
    print("psnr",psnr)
    print("type", type(psnr))
    print("shape",psnr.shape)
    # print(np.unique(psnr))
    print('---------------------------')

    # reconstructed frame
    reconframe = graph.get_tensor_by_name(prefix + 'ReconFrame:0')

    with tf.compat.v1.Session(graph=graph) as sess:

        # im1 = imread(input_path)
        # im2 = imread(refer_path)
        # im1 = im1 / 255.0
        # im2 = im2 / 255.0
        # im1 = np.expand_dims(im1, axis=0)
        # im2 = np.expand_dims(im2, axis=0)
        print('---------------------------')

        # Load and preprocess the images
        image_path1 = "path_to_image1.jpg"
        image_path2 = "path_to_image2.jpg"

        im1 = tf.io.read_file(image_path1)
        im1 = tf.image.decode_image(im1, channels=3)
        im1 = tf.image.convert_image_dtype(im1, tf.float32)

        im2 = tf.io.read_file(image_path2)
        im2 = tf.image.decode_image(im2, channels=3)
        im2 = tf.image.convert_image_dtype(im2, tf.float32)

        # Expand dimensions to simulate a batch
        im1_batch = tf.expand_dims(im1, axis=0)
        im2_batch = tf.expand_dims(im2, axis=0)

        # im1 = tf.image.convert_image_dtype(im1, tf.float32)
        # im1 = im1 / 255.0  # Normalize pixel values to [0, 1]
        # im2 = tf.image.convert_image_dtype(im2, tf.float32)
        # im2 = im2 / 255.0 # Normalize pixel values to [0, 1]

        print("im1 type", type(im1))
        print("im1 shape", tf.shape(im1))
        print("im2 type", type(im2))
        print("im2 shape", tf.shape(im2))
        print('---------------------------')

        # # Run your operations directly on the tensors
        # bpp_est, Res_q, Res_prior_q, motion_q, psnr_val, recon_val = [
        #     op.eval() for op in
        #     [bpp, Res, Res_prior, motion, psnr, reconframe]
        # ]

        # Define placeholders
        inputImage = tf.compat.v1.placeholder(tf.float32, shape=[1, None, None, 3], name='input_image')
        previousImage = tf.compat.v1.placeholder(tf.float32, shape=[1, None, None, 3], name='previous_image')

        # Define operations using placeholders
        bpp_est, Res_q, Res_prior_q, motion_q, psnr_val, recon_val = sess.run(
            [bpp, Res, Res_prior, motion, psnr, reconframe],
            feed_dict={
                inputImage: im1_batch,
                previousImage: im2_batch
            })

        # bpp_est, Res_q, Res_prior_q, motion_q, psnr_val, recon_val = sess.run(
        #     [bpp, Res,
        #     Res_prior,
        #     motion,
        #     psnr,
        #     reconframe],
        #     feed_dict={
        #         inputImage: im1,
        #         previousImage: im2
        #     })
    print('---------------------------')
    print('recon_val', recon_val)
    print('bpp_est', bpp_est)
    print('psnr_val', psnr_val)
    print('---------------------------')
    if not os.path.exists(outputfolder):
        os.mkdir(outputfolder)

    with open(outputfolder + 'quantized_res_feature.pkl', 'wb') as f:
        joblib.dump(Res_q, f)

    with open(outputfolder + 'quantized_res_prior_feature.pkl', 'wb') as f:
        joblib.dump(Res_prior_q, f)

    with open(outputfolder + 'quantized_motion_feature.pkl', 'wb') as f:
        joblib.dump(motion_q, f)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--EncoderModel', type=str, dest="loadmodel", default='./model/L256/frozen_model_E.pb', help="encoder model")
    parser.add_argument('--input_frame', type=str, dest="input_path", default='./image/im002.jpg', help="input image path")
    parser.add_argument('--refer_frame', type=str, dest="refer_path", default='./image/im001.jpg', help="refer image path")
    parser.add_argument('--outputpath', type=str, dest="outputfolder", default='./testpkl/', help="output pkl folder")

    args = parser.parse_args()
    encoder(**vars(args))
