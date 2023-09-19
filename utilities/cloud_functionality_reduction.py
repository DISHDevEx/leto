"""
Module to support periphery cloud functionality for any video reduction or reconstruction modules.

This Class is intended to be used only in a With block for context management.
"""
import os
import traceback
from aEye import Aux
import boto3
import os
import logging

class CloudFunctionalityReduction:
    def __init__(self, s3_args, method_args):
        self.aux = Aux()
        self.s3 = boto3.client("s3")
        self.s3_args = s3_args
        self.method_args = method_args

    def __enter__(self):
        """
        Enter method for context management.

        This method is automatically invoked when using the 'with' statement to instantiate
        the CloudFunctionalityReduction class. It logs the instantiation and returns
        the instance itself for context management.

        Returns:
        CloudFunctionalityReduction: The instance of the CloudFunctionalityReduction class.
        """
        logging.info('CloudFunctionalityReduction class instantiated')
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        """
        Exit method for context management.

        This method is automatically invoked when exiting the 'with' statement that
        encapsulates the CloudFunctionalityReduction class. It handles any exceptions
        that may have occurred during the context and performs post-processing reduction.

        Parameters:
        exc_type (type): The type of exception, if any.
        exc_value (Exception): The exception instance, if any.
        tb (traceback): The traceback object, if any.

        Returns:
        bool: True to indicate that the exception, if any, has been handled.
        """
        
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        self.__postprocess_reduction(self.method_args)

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
        """
        Upload the reduction results to an S3 bucket.

        This method loads the reduction results from a local path specified in 'temp_path'
        within 'method_args' and uploads them to an S3 bucket specified by 'output_bucket_s3'
        in 's3_args', using the 'output_prefix_s3' from 'method_args' to define the object's path.

        Parameters:
        s3_args (dict): A dictionary containing S3-related configuration.
            - output_bucket_s3 (str): The name of the S3 bucket to upload to.
        method_args (dict): A dictionary containing method-specific configuration.
            - temp_path (str): The local path where the reduction results are stored.
            - output_prefix_s3 (str): The prefix for the S3 object path.

        Returns:
        None
        """
        result = self.aux.load_local(method_args['temp_path'])
        self.aux.upload_s3(result, bucket=s3_args['output_bucket_s3'], prefix=method_args['output_prefix_s3'])


    def __postprocess_reduction(self, method_args):
        """
        Perform post-processing tasks on the reduction results.

        This method sets the local path to the one specified in 'temp_path' within 'method_args'
        and then cleans up any temporary files or resources related to the reduction process.

        Parameters:
        method_args (dict): A dictionary containing method-specific configuration.
            - temp_path (str): The local path where the reduction results are stored.

        Returns:
        None
        """

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