import boto3
import json

# Create a Lambda client
lambda_client = boto3.client('lambda', region_name='your_region')

# Lambda function name
function_name = 'your_lambda_function_name'

# Payload data
payload = {
    "bucket_name": "leto-dish",
    "folder_path": "reduced-videos/ffmpeg-resolution-downsampler-480p-lanczos",
    "dynamodb_table" : "test_table"
    # Add any other payload data your Step Function expects
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
