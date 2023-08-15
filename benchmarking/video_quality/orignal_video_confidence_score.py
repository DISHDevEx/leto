import boto3
import json
# Initialize the Boto3 Step Functions client
client = boto3.client('stepfunctions')

# Define your payload
payload = {
    "bucket_name": "leto-dish",
    "folder_path": "reduced-videos/ffmpeg-resolution-downsampler-480p-lanczos",
    "dynamodb_table" : "test_table"
    # Add any other payload data your Step Function expects
}

# Start the execution of the Step Function with the payload
response = client.start_execution(
    stateMachineArn='arn:aws:states:us-east-1:064047601590:stateMachine:leto_downstream_model_scores',
    input=json.dumps(payload)
)

# Print the execution ARN
print("Execution ARN:", response['executionArn'])
