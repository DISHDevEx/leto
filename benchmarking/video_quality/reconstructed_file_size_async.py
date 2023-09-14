"""This module generates reconstructed_file_sizes for dynamodb ."""
import subprocess
import sys
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# Add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler

class FileSizeUploader:
    """
    A class for uploading file sizes and associated information to DynamoDB.

    Attributes:
    ----------
        bucket_name (str): The name of the S3 bucket containing the files.
        table_name (str): The name of the DynamoDB table to upload data to.
    """

    def __init__(self, bucket_name, table_name):
        """
        Initialize the FileSizeUploader instance.

        Args:
            bucket_name (str): The name of the S3 bucket containing the files.
            table_name (str): The name of the DynamoDB table to upload data to.
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def get_file_size(self, s3_key):
        """
        Retrieve the size of a file in the S3 bucket.

        Args:
        ----------
            s3_key (str): The S3 key (path) of the file.

        Returns:
        ----------
            int: The size of the file in bytes, or None if an error occurred.
        """
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            size = response['ContentLength']
            return size
        except Exception as e:
            print(f"Error getting file size for {s3_key}: {e}")
            return None

    def upload_to_dynamodb(self, file_path, size):
        """
        Upload file information to DynamoDB.

        Args:
        ----------
            file_path (str): The path of the file.
            size (int): The size of the file in bytes.

        Returns:
        ----------
            dict: The response from the DynamoDB put_item operation, or None if an error occurred.
        """
        try:
            print(file_path)
            reconstructed_folder = file_path.split("/")[1]
            response = self.table.put_item(Item={'video_location': file_path,
                                                 'reconstructed_file_size': str(size),
                                                 'reconstructed_method': reconstructed_folder})
            print(f"Uploaded {file_path} reduced method {reconstructed_folder} to DynamoDB with size {size} bytes.")
            return response
        except Exception as e:
            print(f"Error uploading to DynamoDB: {e}")
            return None

    def process_and_upload(self, file_locations):
        """
        Process and upload file information for a list of file locations.

        Args:
        ----------
            file_locations (list): List of file locations (S3 keys) to process and upload.

        Returns:
        ----------
            None
        """
        for location in file_locations:
            size = self.get_file_size(location)
            if size is not None:
                self.upload_to_dynamodb(location, size)

    def get_s3_file_locations(self, directory_key):
        """
        Retrieve a list of S3 file locations (keys) for a given directory.

        Args:
        ----------
            directory_key (str): The directory key in the S3 bucket.

        Returns:
        ----------
            list: List of S3 file locations (keys).
        """
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=directory_key)
            full_file_locations = [f"s3://{self.bucket_name}/{obj['Key']}" for obj in response.get('Contents', [])]
            file_locations = [obj['Key'] for obj in response.get('Contents', [])]
            file_locations = [file for file in file_locations if file.endswith("mp4")]
            return file_locations
        except Exception as e:
            print(f"Error getting S3 file locations: {e}")
            return []


if __name__ == "__main__":
    # Initialize configuration and perform the file size upload
    config = ConfigHandler('benchmarking.reconstructed_file_size_async')
    s3_args = config.s3
    method_args = config.method


    # Initialize the S3 client
    s3 = boto3.client('s3')

    # List all objects in the bucket
    objects = s3.list_objects_v2(Bucket=s3_args['input_bucket_s3'],
                                 Prefix=method_args['directory_for_evaluation'], 
                                 Delimiter='/')

    # Extract subfolder names
    subfolder = [prefix['Prefix'] for prefix in objects.get('CommonPrefixes', [])]

    # and sanity check
    file_locations = [file for file in subfolder if file.startswith("reconstructed")]

    # Initialize and use the FileSizeUploader on all folders in file_locations
    for  folder in file_locations:       
        table_name = method_args['table_name']
        uploader = FileSizeUploader(s3_args['input_bucket_s3'], table_name)
        s3_file_locations = uploader.get_s3_file_locations(folder)
        uploader.process_and_upload(s3_file_locations)
