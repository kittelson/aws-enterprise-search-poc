import boto3
import os

s3 = boto3.client('s3')
bucket_name = 'enterprise-search-poc-57447'
new_folder = 'entity_analysis/'

# Define the maximum sizes for each file type
max_sizes = {
    '.txt': 10 * 1024,  # 10KB
    '.pdf': 5 * 1024 * 1024,  # 5MB
    '.docx': 1 * 1024 * 1024,  # 1MB
    '.doc': 1 * 1024 * 1024,  # 1MB
}

# List all files in the bucket
paginator = s3.get_paginator('list_objects_v2')
pages = paginator.paginate(Bucket=bucket_name)

for page in pages:
    for obj in page['Contents']:
        file_key = obj['Key']
        file_size = obj['Size']
        file_extension = os.path.splitext(file_key)[1]

        # Check if the file type is one of the specified types and its size is within the limit
        if file_extension in max_sizes and file_size <= max_sizes[file_extension]:
            # Copy the file to the new folder
            copy_source = {
                'Bucket': bucket_name,
                'Key': file_key
            }
            new_key = new_folder + os.path.basename(file_key)
            s3.copy(copy_source, bucket_name, new_key)
            print(f"Copied {file_key} to {new_key}")