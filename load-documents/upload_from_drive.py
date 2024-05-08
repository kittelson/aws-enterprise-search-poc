import boto3
import os
import time

BUCKET_NAME = "enterprise-search-poc-57447"
LOCAL_DIR = "/Users/ryangallagher/projects/documentation/ICE-tool"


def upload_files_to_s3(bucket_name, local_folder_path):
    s3 = boto3.client('s3')
    allowed_extensions = {'docx', 'pdf', 'xlsx', 'xls', 'doc', 'txt', 'ppt', 'pptx'}
    one_year_ago = time.time() - 60*60*24*365  # Time one year ago

    # Ensure local_folder_path ends with '/'
    if not local_folder_path.endswith('/'):
        local_folder_path += '/'

    for root, dirs, files in os.walk(local_folder_path):
        for file in files:
            _, extension = os.path.splitext(file)
            if extension[1:] in allowed_extensions:  # remove the leading dot from the extension
                local_file = os.path.join(root, file)
                if os.path.getmtime(local_file) >= one_year_ago:  # File has been modified in the last year

                    s3_key = local_file[len(local_folder_path):]

                try:
                    s3.upload_file(local_file, bucket_name, s3_key)
                    print(f"Uploaded {local_file} to {bucket_name}/{s3_key}")
                except Exception as e:
                    print(f"Unable to upload {local_file}. Reason: {e}")
            else:
                print(f"Skipping {file} due to unsupported file type.")


# Usage
upload_files_to_s3(BUCKET_NAME, LOCAL_DIR)
