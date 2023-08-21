import subprocess
import sys
import boto3
import json

# get git repo root level
root_path = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler

config = ConfigHandler('benchmarking.yolo_confidence')
s3 = config.s3
method = config.method

# Create a Lambda client
lambda_client = boto3.client('lambda', region_name=s3['region'])

# Lambda function name

function_name = method['function_name']

# Payload data
payload = {
    "bucket_name": s3['input_bucket_s3'],
    "folder_path": method['folder_path'],
    "dynamodb_table" : method['dynamodb_table']
}

# Call the Lambda function
response = lambda_client.invoke(
    FunctionName=function_name,
    InvocationType='RequestResponse',  # Use 'Event' for asynchronous invocation
    Payload=json.dumps(payload)
)

# Process the response
response_payload = json.loads(response['Payload'].read().decode('utf-8'))
print("Lambda Response:", response_payload)
