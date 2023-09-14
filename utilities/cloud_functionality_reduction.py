"""
Module to support periphery cloud functionality for any video reduction or reconstruction modules.
"""
import os
import traceback
from aEye import Aux
import boto3
import cv2
import shutil
import tempfile
import os
import logging

class CloudFunctionalityReduction:
    def __init__(self, s3_args, method_args):
        self.aux = Aux()
        self.s3 = boto3.client("s3")
        self.s3_args = s3_args
        self.method_args = method_args

    def __enter__(self):
        logging.info('CloudFunctionalityReduction class instantiated')
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.postprocess_reduction(self.method_args)

        return True

    def preprocess_reduction(self, s3_args, method_args):
        """

        Method that downloads videos from s3 and returns a list of video objects.

        Parameters
        ----------
        s3_args: dict
            Defines the s3 bucket params.
        method_args: dict
            Defines reduction technique specific args.

        Returns
        -------
        video_list: list[aEye.Video]
            List of video objects.

        """
        os.mkdir(method_args['temp_path'])
        video_list = self.aux.load_s3(s3_args['input_bucket_s3'], method_args['input_prefix_s3'])
        return video_list

    def upload_reduction(self, s3_args, method_args):
        
        result = self.aux.load_local(method_args['temp_path'])
        self.aux.upload_s3(result, bucket=s3_args['output_bucket_s3'], prefix=method_args['output_prefix_s3'])


    def postprocess_reduction(self, method_args):

        self.aux.set_local_path(method_args['temp_path'])
        self.aux.clean()

    def download_model(self, s3_args, method_args ):
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