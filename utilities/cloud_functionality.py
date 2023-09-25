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

class CloudFunctionality:
    def __init__(self, s3_args, method_args, config_section):
        """
        Initialize a CloudFunctionality instance.

        Args:
            s3_args (dict): AWS S3 configuration parameters.
            method_args (dict): Method-specific arguments.
            config_section (str): Configuration section used from configuration file.

        Attributes:
            aux (Aux): Aux class instance for auxiliary tasks.
            s3 (boto3.client): Amazon S3 client for AWS S3 services.
            s3_args (dict): AWS S3 configuration parameters.
            method_args (dict): Method-specific arguments.
            config_section (str): Configuration section used.

        Example:
            CloudFunctionality is to be used in a "with" clause.
            Initialize CloudFunctionality with configs from ConfigHandler:
            
            >>> config = ConfigHandler("reduction.fps_bitrate")
            >>> s3_args = config.s3
            >>> method_args = config.method
            >>> section_name = config.method_section
            >>> with CloudFunctionality(s3_args, method_args, section_name) as cloud_functionality:
        """
        self.aux = Aux()
        self.s3 = boto3.client("s3")
        self.s3_args = s3_args
        self.method_args = method_args
        self.config_section = config_section

    def __enter__(self):
        """
        Enter method for context management.

        This method is automatically invoked when using the 'with' statement to instantiate
        the CloudFunctionality class. It logs the instantiation and returns
        the instance itself for context management.

        Returns:
        CloudFunctionality: The instance of the CloudFunctionality class.
        """
        logging.info('CloudFunctionality class instantiated')
        return self
    
    def __exit__(self, exc_type, exc_value, tb):
        """
        Handle the context manager's exit operations.

        This method is automatically called when exiting a context managed by the CloudFunctionality class.

        Args:
            exc_type (type): The type of exception raised (or None if no exception).
            exc_value (Exception): The exception instance raised (or None if no exception).
            tb (traceback): The traceback information for the exception (or None if no exception).

        Returns:
            bool: True to indicate successful handling of the context manager's exit.

        Note:
            If an exception is raised within the context managed by CloudFunctionality, it will be printed to the
            standard error using the traceback module. Depending on the 'config_section', this method may also
            trigger post-processing operations.

        Example:
            This method is typically used as part of a context manager and is not called directly by users.
        """
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
        
        if "reduction" in self.config_section:
            self.__postprocess_reduction(self.method_args)
        elif "reconstruction" in self.config_section:
            self.__postprocess_reconstruction(self.method_args)

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

    def __postprocess_reconstruction(self, method_args):
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