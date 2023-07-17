"""
Module contains the Aux class that handles the loading and uploading of videos. This class also has the feature to executing all ffmpeg labels and write new videos.

"""

from leto.video import Video
import boto3
import tempfile
import os
import subprocess
import logging
from static_ffmpeg import run

#Please comment this out when setting up a docker image.
#This will fail when we use the docker image in the lambda function on AWS.
ffmpeg, ffprobe = run.get_or_fetch_platform_executables_else_raise()

class Aux:
    """
    Aux is the class that works as a pipeline to load, write, and upload all video from S3 bucket.

    Attributes
    ----------
        _s3: botocore.client.S3
            An internal variable to talk to S3.

        _temp_folder: string
            An internal variable for temp folder path.

        _local_path: string
            An internal variable for local folder path.


    Methods
    -------
        load_s3(bucket, prefix) -> list[Video]:
            Loads in video files as Video classes into a list from S3.

        load_local(path) -> list[Video]:
            Loads in video files as Video classes into a list from local machine.

        write() -> None:
            Execute and run the video's labels and write the video to temp folder.

        execute_label_and_write_local(video_list) -> List[Video]
            Super important function to execute any pending labels on video list. This is how the FFmpeg
            command is run, and if further processing is needed, it returns a processed video list.


    """

    def __init__(self):

        self._s3 = boto3.client('s3')
        self._temp_folder = tempfile.mkdtemp(dir="")
        self._local_path = None

    def load_s3(self, bucket, prefix):
        """
        This method will load the video files from S3 and return them
        into a list of video classes.

         Parameters
        ----------

        bucket: string
            The bucket name to path into S3 to get the video files.
        prefix: string
            The folder name where the video files belong in the S3 bucket.

        Returns
        -------

        video_list: list
            The list of all video files loaded from S3 bucket.
        """

        video_list = []
        result = self._s3.list_objects(Bucket=bucket, Prefix=prefix)
        for i in result["Contents"]:
            # When we request from S3 with the input parameters, the prefix folder will also pop up as a object.
            # This if-statement is to skip over the folder object since we are only interested in the video files.
            if i["Key"] == prefix:
                continue

            title = i["Key"].split(prefix)[1]
            new_video = Video(bucket=bucket, key=i["Key"], title=title)
            if self._local_path is None:
                new_video.path = self._temp_folder
            else:
                new_video.path = self._local_path
            video_list.append(new_video)
        logging.info(f"successfully load the video files from S3 bucket: s3://{bucket}/{prefix}/")

        return video_list

    def load_local(self, path):
        """
        This method will load the video files from the given path parameters.
        This method will recognize whether a folder or a single file is given.

        Parameters
        ----------

        path: string
            The bucket name to path into local to get the video files.

        Returns
        -------

        video_list: list
            The list of all video files loaded from local bucket.
        """
        video_list = []

        # video_list = [Video(file=  path + i, title=i) for i in os.listdir(path) if Video(file=  path + i, title=i)]

        if os.path.isdir(path):
            for i in os.listdir(path):
                new_vid = Video(file=path + i, title=i)
                new_vid.path = self._temp_folder
                video_list.append(new_vid)

        else:
            dummy = path.replace('/', ' ').strip()
            title = dummy.split(' ')[-1]
            new_vid = Video(file=path, title=title)
            new_vid.path = self._temp_folder
            video_list.append(new_vid)

        logging.info(f"successfully load the video files from local path: {path}")

        return video_list

    def upload_s3(self, video_list, bucket, prefix='modified/'):
        """
        This method will push modified video list to the S3 bucket and delete all video files from local temp folder.

        Parameters
        ----------
            video_list: list
                The list of video that needs to be uploaded.

            bucket: string
                The bucket name/path to upload on S3.

            prefix: string
                The subfolder name that the video list will be uploaded to.

        """

        s3 = boto3.client('s3')
        for video in video_list:
            # if video.get_label() != "":
            if not self._local_path:
                path = self._temp_folder + '/' + video.get_output_title()
            else:
                path = self._local_path + '/' + video.get_output_title()
            s3.upload_file(path, bucket, prefix + video.get_output_title())

        logging.info(f"successfully upload the output files S3 bucket: s3://{bucket}/{prefix}/")

    def execute_label_and_write_local(self, video_list, path=None):
        """
        This method will execute and write new videos based on all videos that contain ffmpeg labels.
        This will default write the output video into a temp folder unless the user provide a local path.

        Parameters
        ----------
            video_list: list
                The list of video that needs to be executed and wrote as output files.

            local: string
                The path to write the output videos to.

        """

        # If the user prompts this method with a specific path, then this will save it into the internal variable.
        # This will check if there exists an local path internal. If there exists, then we will write video files there.
        if path is None:
            path = self._local_path if self._local_path else self._temp_folder

        else:
            self.set_local_path(path)

        list_video = []

        for video in video_list:
            # This if statement will skip over any untouched videos.
            # if video.get_label() != "":

            if video.out == '':
                source = video.get_presigned_url()
            else:
                source = video.out
            if len(video.complex_filter) > 0:
                video.create_complex_filter(video)
            command = f"{ffmpeg} -y -i {source} {video.get_label()} {path}/{video.get_output_title()}"
            subprocess.run(command, shell=True)
            logging.info(command)
            # print(command)  # REALLY useful for debug
            new_path = video.get_output_title()
            video.reset_label()
            new_video = Video(f'{path}/{video.get_output_title()}', title=f'{video.get_output_title()}')
            new_video.set_output(f"'{path}/{new_path}'")
            list_video.append(new_video)

        logging.info(f"successfully write the output video files to path: {path}")

        return list_video

    def clean(self, path=None):
        """
        This method will delete the temp folder and all video files in it from local machine.

        Parameters
        ----------
        path : str
            The path to set

        Returns
        ----------
        """
        if path is None:
            path = self._local_path if self._local_path else self._temp_folder

        for (path, _, files) in os.walk(path, topdown=True):
            for video in files:
                os.remove(f'{path}/{video}')

        os.rmdir(path)

        logging.info("successfully remove the temp folder from local machine")

    def set_local_path(self, path):
        """
        This method will set the path as an internal variable

        Parameters
        ----------
        path : str
            The path to set

        Returns
        ----------

        """
        self._local_path = path