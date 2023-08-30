"""This module generates reduced_file_sizes for dynamodb ."""
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
    A class for uploading file sizes and related information to DynamoDB.
    """

    def __init__(self, bucket_name, table_name):
        """
        Initializes the FileSizeUploader.

        Args:
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
        Retrieves the size of a file in bytes from S3.

        Args:
        ----------
            s3_key (str): The S3 key of the file.

        Returns:
        ----------
            int or None: The size of the file in bytes, or None if an error occurs.
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
        Uploads file information to DynamoDB.

        Args:
        ----------
            file_path (str): The path of the file.
            size (int): The size of the file in bytes.

        Returns:
        ----------
            dict or None: The response from DynamoDB, or None if an error occurs.
        """
        try:
            reduced_folder = file_path.split("/")[1]
            response = self.table.put_item(Item={'video_location': file_path,
                                                 'reduced_file_size': str(size),
                                                 'reduced_method': reduced_folder})
            print(f"Uploaded {file_path} reduced method {reduced_folder} to DynamoDB with size {size} bytes.")
            return response
        except Exception as e:
            print(f"Error uploading to DynamoDB: {e}")
            return None

    def process_and_upload(self, file_locations):
        """
        Processes file locations and uploads information to DynamoDB.

        Args:
        ----------
            file_locations (list): List of S3 file locations.

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
        Retrieves S3 file locations from a specific directory.

        Args:
        ----------
            directory_key (str): The S3 directory key.

        Returns:
        ----------
            list: List of S3 file locations.
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
    config = ConfigHandler('benchmarking.reduced_file_size')
    s3_args = config.s3
    method_args = config.method

    # Initialize the S3 client
    s3 = boto3.client('s3')

    # List all objects in the bucket
    objects = s3.list_objects_v2(Bucket='leto-dish', Prefix='reconstructed-videos/', Delimiter='/')

    # # Extract subfolder names
    subfolders = [prefix['Prefix'] for prefix in objects.get('CommonPrefixes', [])]

    file_locations = [file for file in subfolders if file.startswith("reconstructed")]

    # Initialize and use the FileSizeUploader on all folders in file_locations
    for  folder in file_locations:       
        table_name = method_args['table_name']
        uploader = FileSizeUploader(s3_args['input_bucket_s3'], table_name)
        s3_file_locations = uploader.get_s3_file_locations(folder)
        uploader.process_and_upload(s3_file_locations)


