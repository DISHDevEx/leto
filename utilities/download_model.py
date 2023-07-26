'''
Module to download any model file from s3 to a local path.
'''
import boto3

def download_model(local_path, bucket_name, key):
    """
    Downloads any model file from s3 to a local path.

    Parameters
    ----------

    local_path: string
        Path where we want to store object locally
    bucket_name: string
        The bucket name where the files belong in the S3 bucket.
    key: string
        The name of the object and any preceeding folders.
    """
    s3 = boto3.client("s3")
    with open(local_path, "wb") as file:
        s3.download_fileobj(bucket_name, key, file)