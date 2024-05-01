import boto3
import os

BUCKET_NAME = "enterprise-search-poc-57447"
LOCAL_DIR = "/Users/ryangallagher/projects/documentation/ICE-tool"


def upload_files_to_s3(bucket_name, local_folder_path):
    s3 = boto3.client('s3')

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            local_file = os.path.join(root, file)
            s3_key = local_file[len(local_folder_path):]

            try:
                s3.upload_file(local_file, bucket_name, s3_key)
                print(f"Uploaded {local_file} to {bucket_name}/{s3_key}")
            except Exception as e:
                print(f"Unable to upload {local_file}. Reason: {e}")


# Usage
upload_files_to_s3(BUCKET_NAME, LOCAL_DIR)
