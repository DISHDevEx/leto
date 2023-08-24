"""
Module to support periphery cloud functionality for any video reduction or reconstruction modules.
"""
import os
from aEye import Aux
import boto3
import cv2


class CloudFunctionality:
    def __init__(self):
        self.aux = Aux()
        self.s3 = boto3.client("s3")

    def download_model(self, method_args, s3_args):
        """
        Downloads any model file from s3 to a local path.

        Parameters
        ----------
        s3_args: dict
            Defines the s3 bucket params.
        method_args: dict
            Defines reduction technique specific args.
        """

        with open(method_args['local_model_path'], "wb") as file:
            self.s3.download_fileobj(s3_args['model_bucket_s3'], method_args['model_prefix_s3'], file)

    def preprocess_reconstruction(self, s3_args, method_args):
        """
        Method that downloads videos and model from s3 onto local environment.

        Parameters
        ----------
        s3_args: dict
            Defines the s3 bucket params.
        method_args: dict
            Defines reduction technique specific args.
        """

        os.mkdir("./reduced_videos")
        os.mkdir("./reconstructed_videos")

        reduced_video_list = self.aux.load_s3(
            s3_args['input_bucket_s3'], method_args['input_prefix_s3']
        )

        # store the cloud videos locally
        self.aux.execute_label_and_write_local(reduced_video_list, "reduced_videos")

        # Download model.
        if method_args.getboolean('download_model'):
            self.download_model(s3_args, method_args)

    def postprocess_reconstruction(self, s3_args, method_args ):
        """
        Method that moves local video to s3 and deletes
        temporary video folders and model file.

        Parameters
        ----------
        s3_args: dict
            Defines the s3 bucket params.
        method_args: dict
            Defines reduction technique specific args.
        """

        # Load reconstructed video files
        reconstructed_video_list = self.aux.load_local("./reconstructed_videos")

        # Upload reconstructed video files to s3
        self.aux.upload_s3(
            reconstructed_video_list,
            bucket=s3_args['output_bucket_s3'],
            prefix=method_args['output_prefix_s3'],
        )

        # Delete reconstructed_videos folder from local
        self.aux.set_local_path("./reconstructed_videos")
        self.aux.clean()

        self.aux.set_local_path("./reduced_videos")

        # Delete reduced_videos folder from local
        self.aux.clean()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

        # After cleaning videos, delete the pretrained model as well.
        if method_args.getboolean('clean_model'):
<<<<<<< HEAD
            os.remove(method_args['local_model_path'])
=======
            os.remove(method_args['local_model_path'])
