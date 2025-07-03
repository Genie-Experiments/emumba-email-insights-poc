import boto3
import os

# Initialize the S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id="aws_access_key_id",
    aws_secret_access_key="aws_secret_access_key"
)

def download_files_from_bucket(bucket_name, prefix, download_dir):
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)

    # List objects in the bucket with the specified prefix
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

    if "Contents" in response:
        for obj in response["Contents"][:3]:
            file_key = obj["Key"]
            file_path = os.path.join(download_dir, os.path.relpath(file_key, prefix))

            # Create subdirectories if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Download the file
            print(f"Downloading {file_key} to {file_path}")
            s3.download_file(bucket_name, file_key, file_path)
    else:
        print(f"No files found in bucket: {bucket_name} with prefix: {prefix}")

# Example usage
bucket_name = "emumba-email-insights"
company_name='volkswagen_ag'

download_files_from_bucket(bucket_name, f"Prod/{company_name}/attachments/", f's3_data/{company_name}/attachments')
download_files_from_bucket(bucket_name, f"Prod/{company_name}/email_json/", f's3_data/{company_name}/email_json')