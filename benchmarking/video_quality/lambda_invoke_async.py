
import boto3
import json

# def invoke_lambda_and_process_response(function_name, folder_path, table_name, region, bucket_name, request_type):

    # root_path = subprocess.run(
    #     ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    # ).stdout.rstrip("\n")

    # # add git repo path to use all libraries
    # sys.path.append(root_path)

    # from utilities import ConfigHandler

    # # Load configuration using ConfigHandler
    # config = ConfigHandler('benchmarking.mp_confidence')
    # s3_args = config.s3
    # method_args = config.method

# Initialize the S3 client
s3 = boto3.client('s3')

# Create a Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')


# List all objects in the bucket
objects = s3.list_objects_v2(Bucket='leto-dish', Prefix='reduced-videos/', Delimiter='/')

# # Extract subfolder names
subfolders = [prefix['Prefix'] for prefix in objects.get('CommonPrefixes', [])]

file_locations = [file for file in subfolders if file.startswith("reduced")]


# Loop to send multiple asynchronous invocations
for folder in file_locations:

    # Payload data
    payload = {"bucket_name": 'leto-dish',"folder_path": folder ,"dynamodb_table": 'leto_mediapipe'}

    # convert payload to JSON and then convert to utf-8 byte format
    json_data = json.dumps(payload)
    payload_bytes= json_data.encode('utf-8')

    lambda_client.invoke_async(FunctionName='leto-mediapipie',InvokeArgs=payload_bytes)
