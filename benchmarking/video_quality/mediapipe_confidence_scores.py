import sys
import subprocess
from lambda_invoke import invoke_lambda_and_process_response

# get git repo root level
root_path = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, check=False).stdout.rstrip("\n")

# add git repo path to use all libraries
sys.path.append(root_path)

from utilities import ConfigHandler


def main():
    # Load configuration using ConfigHandler
    config = ConfigHandler('benchmarking.mp_confidence')
    s3 = config.s3
    method = config.method

    bucket_name = s3['input_bucket_s3']
    region = s3['region']

    function_name = method['function_name']
    folder_path = method['folder_path']
    table_name = method['dynamodb_table']
    invoke_lambda_and_process_response(function_name, folder_path, table_name, region, bucket_name)


if __name__ == "__main__":
    main()
