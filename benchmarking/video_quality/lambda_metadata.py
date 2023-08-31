import subprocess
import boto3
import os
import json

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):

    """
    Lambda function to process video files, extract metadata, and upload to DynamoDB.

    Args:
        event (dict): The event input to the Lambda function.
        context (object): The Lambda runtime information.

    Returns:
        None
    """

    # take in payload
    bucket_name = event["bucket_name"]
    folder_path = event["folder_path"]
    dynamodb_table = event["dynamodb_table"]
    
    # Retrieve the list of object keys from the specified bucket
    s3_keys = list_object_keys(bucket_name, folder_path)

    # define the dynamoDB table
    table_name = dynamodb_table
    table = dynamodb.Table(table_name)

    for key in s3_keys:
    
        # define local file name and download video to lambda
        local_filename = "/tmp/" + os.path.basename(key)
        s3_client.download_file(bucket_name, key, local_filename)
        
        # get metadata for video, create dict
        command = f"ffprobe {local_filename} -hide_banner -show_streams -v error -print_format json -show_format"
        out = subprocess.check_output(command, shell=True).decode("utf-8")
        metadata_dict = json.loads(out)
        
        # calculate the fps as an int
        fps_fraction = metadata_dict["streams"][0]["r_frame_rate"]
        numerator, denominator = map(int, fps_fraction.split("/"))
        fps = int(numerator / denominator)
        
        # append desired metadata to dynamoDB table        
        try:
            response = table.put_item(
                Item={
                    "video_location": key,
                    "bit_rate": metadata_dict["format"]["bit_rate"],
                    "fps": fps
                }
            )
            print("Uploaded location:", key)
        except Exception as e:
            print("Error uploading key:", key, e)


def list_object_keys(bucket_name, folder_path):

    """
    List object keys within a specified S3 bucket and folder path.

    Args:
        bucket_name (str): The name of the S3 bucket.
        folder_path (str): The path within the bucket to list objects from.

    Returns:
        list: A list of object keys in the specified bucket and folder path.
    """
        
    keys = []
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)
    if "Contents" in response:
        for obj in response["Contents"]:
            keys.append(obj["Key"])
        file_locations = [file for file in keys if file.endswith("mp4")]
    return file_locations
