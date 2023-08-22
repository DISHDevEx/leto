"""

"""
import os
from aEye import Aux
import boto3
import cv2


class CloudFunctionality:
    def __init__(self):
        self.aux = Aux()
        self.s3 = boto3.client("s3")
        
    def preprocess_reduction(self, s3_args, method_args ):
        os.mkdir(method['temp_path'])
        video_list = self.aux.load_s3(s3['input_bucket_s3'], method['input_prefix_s3'])
        return video_list
        
    
    def postprocess_reduction(self, s3_args, method_args):
        result = self.aux.load_local(method['temp_path'])
        self.aux.upload_s3(result, bucket=s3['output_bucket_s3'], prefix=method['output_prefix_s3'])
        self.aux.set_local_path(method['temp_path'])
        self.aux.clean()

    def download_model(self, s3_args, method_args ):
        """
        Downloads any model file from s3 to a local path.

        Parameters
        ----------

        local_path: string
            Path where we want to store object locally
        bucket_name: string
            The bucket name where the files belong in the S3 bucket.
        key: string
            The name of the object and any preceding folders.
        """

        with open(method_args['local_model_path'], "wb") as file:
            self.s3.download_fileobj(s3_args['model_bucket_s3'], method_args['model_prefix_s3'], file)

    def preprocess_reconstruction(self, s3_args, method_args):
        """
        Method that downloads videos and model from s3 onto local environment.
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
            self.download_model(method_args, s3_args)

    def postprocess_reconstruction(self, s3_args, method_args ):
        """
        Method that moves local video to s3 and deletes
        temporary video folders and model file.
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
            os.remove(method_args['local_model_path'])

