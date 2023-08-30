"""
invoke_lambda_async.py

This script invokes an AWS Lambda function asynchronously for each subfolder within a specified S3 bucket.
It extracts subfolder names from the specified bucket's directory, prepares payload data for each subfolder,
and invokes the Lambda function asynchronously with the payload. The script uses configurations loaded from
the 'benchmarking.lambda_invoke_async' section of the configuration file.

Dependencies:
- boto3: Amazon Web Services (AWS) SDK for Python
- subprocess: For executing shell commands
- sys: System-specific parameters and functions
- json: JSON (JavaScript Object Notation) encoding and decoding

Usage:
- Run this script to invoke the specified Lambda function asynchronously for each subfolder in the specified S3 bucket.

Note:
- This script assumes that the AWS credentials and region have been configured using the AWS CLI or environment variables.

"""

import subprocess
import sys
import boto3
import json

def invoke_lambda_async(s3_args, method_args):

    """
    Invoke an AWS Lambda function asynchronously for each subfolder in the specified S3 bucket's directory.

    Parameters:
    - s3_args (dict): A dictionary containing S3-related configuration settings.
    - method_args (dict): A dictionary containing method-specific configuration settings.

    Configuration Details:
    - s3_args:
        - region (str): The AWS region where the S3 bucket and Lambda function are located.
        - input_bucket_s3 (str): The name of the input S3 bucket.
    - method_args:
        - directory_for_evaluation (str): The directory within the input S3 bucket to evaluate.
        - dynamodb_table (str): The name of the DynamoDB table to use for data storage.
        - lambda_function_name (str): The name of the AWS Lambda function to invoke.

    Note:
    - This function uses the provided configuration settings to perform the asynchronous invocations.
    """

    # Initialize the S3 client
    s3 = boto3.client('s3')

    # Create a Lambda client
    lambda_client = boto3.client('lambda', region_name=s3_args['region'])


    # List all objects in the bucket
    objects = s3.list_objects_v2(Bucket=s3_args['input_bucket_s3'], Prefix=method_args['directory_for_evaluation'], Delimiter='/')

    # Extract subfolder names
    subfolder = [prefix['Prefix'] for prefix in objects.get('CommonPrefixes', [])]
    # and perform sanity check
    file_locations = [file for file in subfolder if file.startswith(method_args['directory_for_evaluation'])]


    # Loop to send multiple asynchronous invocations
    for folder in file_locations:

        # Payload data
        payload = {"bucket_name": s3_args['input_bucket_s3'],"folder_path": folder ,"dynamodb_table": method_args['dynamodb_table']}

        # convert payload to JSON and then convert to utf-8 byte format
        json_data = json.dumps(payload)
        payload_bytes= json_data.encode('utf-8')

        lambda_client.invoke_async(FunctionName=method_args['lambda_function_name'] ,InvokeArgs=payload_bytes)


if __name__ == "__main__":

    # get git repo root level
    root_path = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    ).stdout.rstrip("\n")

    # add git repo path to use all libraries
    sys.path.append(root_path)

    from utilities import ConfigHandler

    # Load configuration using ConfigHandler
    config = ConfigHandler('benchmarking.lambda_invoke_async')
    s3_args = config.s3
    method_args = config.method

    invoke_lambda_async(s3_args, method_args)