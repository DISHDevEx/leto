import subprocess
import sys
import boto3
import botocore.config
import json

def invoke_lambda_and_process_response():
    """
    Invokes a Lambda function with specified payload and processes the response.

    This script demonstrates how to invoke an AWS Lambda function with a payload,
    wait for the response, and process the returned payload.

    Note:
    - Before using this script, ensure that the required AWS credentials and configurations
      are properly set up, and that the 'utilities' module and its dependencies are accessible
      in the specified git repository.

    Returns:
        None

    Raises:
        subprocess.CalledProcessError: If there is an error while executing the git command.
        botocore.exceptions.ConfigError: If there is an error in the AWS SDK configuration.
        botocore.exceptions.WaiterError: If waiting for the Lambda function response encounters an error.
        json.JSONDecodeError: If there is an error while decoding the Lambda response payload.

    """
    # get git repo root level
    root_path = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False
    ).stdout.rstrip("\n")

    # add git repo path to use all libraries
    sys.path.append(root_path)

    from utilities import ConfigHandler

    # Load configuration using ConfigHandler
    config = ConfigHandler('benchmarking.mp_confidence')
    s3 = config.s3
    method = config.method

    # Create a Lambda client with custom configuration
    config = botocore.config.Config(
        read_timeout=900,
        connect_timeout=900,
        retries={"max_attempts": 0}
    )
    lambda_client = boto3.client('lambda', region_name=s3['region'], config=config)

    # Lambda function name
    function_name = method['function_name']

    # Payload data
    payload = {
        "bucket_name": s3['input_bucket_s3'],
        "folder_path": method['folder_path'],
        "dynamodb_table": method['dynamodb_table']
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

# Invoke the function when this script is run
if __name__ == "__main__":
    invoke_lambda_and_process_response()
