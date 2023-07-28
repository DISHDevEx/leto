from aEye import Aux
import boto3

Class CloudFunctionality:

    def __init__():
        self.aux = Aux()

    def download_model(self,local_path, bucket_name, key):
        """
        Downloads any model file from s3 to a local path.

        Parameters
        ----------

        local_path: string
            Path where we want to store object locally
        bucket_name: string
            The bucket name where the files belong in the S3 bucket.
        key: string
            The name of the object and any preceeding folders.
        """
        s3 = boto3.client("s3")
        with open(local_path, "wb") as file:
            s3.download_fileobj(bucket_name, key, file)

    def preprocess(self,args):
        '''
        Method that downloads videos and model from s3 onto local environment.
        '''

        os.mkdir('./reduced_videos')
        os.mkdir('./reconstructed_videos')

        reduced_video_list = self.aux.load_s3(args.input_bucket_s3, args.input_prefix_s3)

        #store the cloud videos locally
        self.aux.execute_label_and_write_local(reduced_video_list, 'reduced_videos')

        # Download model.
        self.download_model(args.local_model_path, args.model_bucket_s3, args.model_prefix_s3)

    def postprocess(self,args):
        '''
        Method that moves local video to s3 and deletes
        temporary video folders and model file.
        '''

        # Load reconstructed video files
        reconstructed_video_list = self.aux.load_local('./reconstructed_videos')

        self.aux.set_local_path('./reconstructed_videos')

        # Upload reconstructed video files to s3
        self.aux.upload_s3(reconstructed_video_list, bucket = args.output_bucket_s3, prefix = args.output_prefix_s3)

        # Delete reconstructed_videos folder from local
        self.aux.clean()

        self.aux.set_local_path('./reduced_videos')

        # Delete reduced_videos folder from local
        self.aux.clean()

        # Close all OpenCV windows
        cv2.destroyAllWindows()

        #After cleaning videos, delete the pretrained model as well.
        os.remove(args.model_path)