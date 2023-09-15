"""
Module to support periphery cloud functionality for any video reduction or reconstruction modules.
"""
import os
import traceback
from aEye import Aux
import boto3
import cv2
import logging


class CloudFunctionalityReconstruction:
    def __init__(self, s3_args, method_args):
        self.aux = Aux()
        self.s3 = boto3.client("s3")
        self.s3_args = s3_args
        self.method_args = method_args

    def __enter__(self):
        """
        Enter method for context management.

        This method is automatically invoked when using the 'with' statement to instantiate
        the CloudFunctionalityReconstruction class. It logs the instantiation and returns
        the instance itself for context management.

        Returns:
        CloudFunctionalityReconstruction: The instance of the CloudFunctionalityReconstruction class.
        """
        logging.info('CloudFunctionalityReconstruction class instantiated')
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        """
        Exit method for context management.

        This method is automatically invoked when exiting the 'with' statement that
        encapsulates the CloudFunctionalityReconstruction class. It handles any exceptions
        that may have occurred during the context, prints a traceback if an exception is
        raised, and performs post-processing of video reconstruction using 'postprocess_reconstruction'.

        Parameters:
        exc_type (type): The type of exception, if any.
        exc_value (Exception): The exception instance, if any.
        tb (traceback): The traceback object, if any.

        Returns:
        bool: True to indicate that the exception, if any, has been handled.
        """
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.postprocess_reconstruction(self.method_args)

        return True

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


    def upload_reconstruction(self, s3_args, method_args):
        """
        Upload reconstructed video files to an S3 bucket.

        This method loads the reconstructed video files from the local 'reconstructed_videos' directory,
        which is assumed to be at "./reconstructed_videos". It then uploads these video files to an S3
        bucket specified by 'output_bucket_s3' in 's3_args', using the 'output_prefix_s3' from 'method_args'
        to define the object's path.

        Parameters:
        s3_args (dict): A dictionary containing S3-related configuration.
            - output_bucket_s3 (str): The name of the S3 bucket to upload to.
        method_args (dict): A dictionary containing method-specific configuration.
            - output_prefix_s3 (str): The prefix for the S3 object path.

        Returns:
        None
        """        
        # Load reconstructed video files
        reconstructed_video_list = self.aux.load_local("./reconstructed_videos")

        # Upload reconstructed video files to s3
        self.aux.upload_s3(
            reconstructed_video_list,
            bucket=s3_args['output_bucket_s3'],
            prefix=method_args['output_prefix_s3'],
        )

    def postprocess_reconstruction(self, method_args):
        """
        Perform post-processing tasks after video reconstruction.

        This method cleans up the local 'reconstructed_videos' directory, which is assumed to be located
        at "./reconstructed_videos", by deleting it. This is typically done after the video reconstruction
        process to remove temporary or intermediate files.

        Parameters:
        method_args (dict): A dictionary containing method-specific configuration (not used in this method).

        Returns:
        None
        """

        # Delete reconstructed_videos folder from local
        self.aux.set_local_path("./reconstructed_videos")
        self.aux.clean()

        # Delete reduced_videos folder from local
        self.aux.set_local_path("./reduced_videos")
        self.aux.clean()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

        # After cleaning videos, delete the pretrained model as well.
        if method_args.getboolean('clean_model'):
            os.remove(method_args['local_model_path'])


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
