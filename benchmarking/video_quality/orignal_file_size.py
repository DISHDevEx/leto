import os
import subprocess
import sys
import boto3
import logging
logging.info("running reduction module")

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler

class FileSizeUploader:
    def __init__(self, bucket_name, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name

    def get_file_size(self, s3_key):
        try:
            response = self.s3.head_object(Bucket=self.bucket_name, Key=s3_key)
            size = response['ContentLength']
            return size
        except Exception as e:
            print(f"Error getting file size for {s3_key}: {e}")
            return None

    def upload_to_dynamodb(self, file_path, size):
        try:
            response = self.table.put_item(Item={'video_location': file_path, 'file_size': str(size)})
            print(f"Uploaded {file_path} to DynamoDB with size {size} bytes.")
            return response
        except Exception as e:
            print(f"Error uploading to DynamoDB: {e}")
            return None

    def process_and_upload(self, file_locations):
        for location in file_locations:
            size = self.get_file_size(location)
            if size is not None:
                self.upload_to_dynamodb(location, size)

    def get_s3_file_locations(self, directory_key):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=directory_key)
            full_file_locations = [f"s3://{self.bucket_name}/{obj['Key']}" for obj in response.get('Contents', [])]
            file_locations = [obj['Key'] for obj in response.get('Contents', [])]
            return file_locations
        except Exception as e:
            print(f"Error getting S3 file locations: {e}")
            return []



config = ConfigHandler('benchmarking.original_file_size')
s3 = config.s3
method = config.method


uploader = FileSizeUploader(s3['input_bucket_s3'], method['table_name'])
directory_key = method['directory_key']
s3_file_locations = uploader.get_s3_file_locations(directory_key)
uploader.process_and_upload(s3_file_locations)
