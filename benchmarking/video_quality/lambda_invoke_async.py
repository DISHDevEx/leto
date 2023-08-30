
import subprocess
import sys
import boto3
import json

def invoke_lambda_async(s3_args, method_args):

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