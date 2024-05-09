import boto3
import os
import time

BUCKET_NAME = "enterprise-search-poc-57447"
LOCAL_DIR = "H:\\30"


def upload_files_to_s3(bucket_name, local_folder_path):
    s3 = boto3.client('s3')
    allowed_extensions = {'docx', 'pdf', 'xlsx', 'xls', 'doc', 'txt', 'ppt', 'pptx'}
    one_year_ago = time.time() - 60*60*24*365  # Time one year ago
    max_file_size = 50 * 1024 * 1024  # 50MB in bytes
    s3_folder_path = "projects/30/"  # Desired S3 path
    allowed_dirs = ['admin/p', 'admin/p/08_Final Files']

    # Ensure local_folder_path ends with '/'
    if not local_folder_path.endswith('/'):
        local_folder_path += '/'

    for root, dirs, files in os.walk(local_folder_path):
        if root.replace("\\", "/").endswith(tuple(allowed_dirs)):
            for file in files:
                _, extension = os.path.splitext(file)
                if extension[1:] in allowed_extensions:  # remove the leading dot from the extension
                    local_file = os.path.join(root, file)
                    if os.path.getmtime(local_file) >= one_year_ago:  # File has been modified in the last year
                        if os.path.getsize(local_file) <= max_file_size:  # File is not larger than 50MB
                            relative_path = os.path.relpath(root, local_folder_path).replace("\\", "/")
                            s3_key = s3_folder_path + relative_path + "/" + file

                            try:
                                s3.upload_file(local_file, bucket_name, s3_key)
                                print(f"Uploaded {local_file} to {bucket_name}/{s3_key}")
                            except Exception as e:
                                print(f"Unable to upload {local_file}. Reason: {e}")
                        else:
                            print(f"Skipping {file} due to file size.")
                    else:
                        print(f"Skipping {file} due to last modification date.")
                else:
                    print(f"Skipping {file} due to unsupported file type.")
        else:
            print(f"Skipping files in {root} as it's not in the allowed directories.")


# Usage
upload_files_to_s3(BUCKET_NAME, LOCAL_DIR)
