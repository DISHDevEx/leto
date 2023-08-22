"""This module generates orignal_file_sizes for dynamodb ."""
import subprocess
import sys
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler

class FileSizeUploader:
    """Utility class for uploading file sizes to DynamoDB from S3."""

    def __init__(self, bucket_name, table_name):
        """
        Initialize the FileSizeUploader.

        Parameters:
        ----------
            bucket_name (str): The name of the S3 bucket.
            table_name (str): The name of the DynamoDB table.
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def get_file_size(self, s3_key):
        """
        Get the size of a file in S3.

        Parameters:
        ----------
            s3_key (str): The S3 key of the file.

        Returns:
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

        Parameters:
        ----------
            file_path (str): The path of the file.
            size (int): The size of the file in bytes.

        Returns:
            dict or None: The response from DynamoDB, or None if an error occurred.
        """
        try:
            response = self.table.put_item(Item={'video_location': file_path,
                                                 'original_file_size': str(size)})
            print(f"Uploaded {file_path} to DynamoDB with size {size} bytes.")
            return response
        except Exception as e:
            print(f"Error uploading to DynamoDB: {e}")
            return None

    def process_and_upload(self, file_locations):
        """
        Process and upload file sizes for the given S3 file locations.

        Parameters:
        ----------
            file_locations (list): List of S3 file locations.

        Returns:
            None
        """
        for location in file_locations:
            size = self.get_file_size(location)
            if size is not None:
                self.upload_to_dynamodb(location, size)

    def get_s3_file_locations(self, directory_key):
        """
        Get a list of S3 file locations within a directory.

        Parameters:
        ----------
            directory_key (str): The S3 key of the directory.

        Returns:
            list: List of S3 file locations.
        """
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=directory_key)
            full_file_locations = [f"s3://{self.bucket_name}/{obj['Key']}" for obj in response.get('Contents', [])]
            file_locations = [obj['Key'] for obj in response.get('Contents', [])]
            return file_locations[1:]
        except Exception as e:
            print(f"Error getting S3 file locations: {e}")
            return []


if __name__ == "__main__":
    # Load configuration
    config = ConfigHandler('benchmarking.original_file_size')
    s3 = config.s3
    method = config.method

    # Initialize and use the FileSizeUploader
    uploader = FileSizeUploader(s3['input_bucket_s3'], method['table_name'])
    directory_key = method['directory_key']
    s3_file_locations = uploader.get_s3_file_locations(directory_key)
    uploader.process_and_upload(s3_file_locations)
