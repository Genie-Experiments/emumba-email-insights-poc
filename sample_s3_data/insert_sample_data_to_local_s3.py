import boto3
import os

# Initialize the S3 client for LocalStack
s3 = boto3.client(
    "s3",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    endpoint_url="http://localhost:4566"  # LocalStack endpoint
)

def upload_files_to_bucket(bucket_name, prefix, local_dir):
    # Iterate through files in the local directory
    for root, _, files in os.walk(local_dir):
        for file in files:
            file_path = os.path.join(root, file)
            s3_key = os.path.join(prefix, os.path.relpath(file_path, local_dir))

            # Upload the file
            print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
            s3.upload_file(file_path, bucket_name, s3_key)

# Example usage
bucket_name = "emumba-email-insights"
company_name='volkswagen_ag'

upload_files_to_bucket(bucket_name, f"Prod/{company_name}/attachments/", f's3_data/{company_name}/attachments')
upload_files_to_bucket(bucket_name, f"Prod/{company_name}/email_json/", f's3_data/{company_name}/email_json')

upload_files_to_bucket(bucket_name, "Prod/audi_ag/attachments/", 's3_data/attachments')
upload_files_to_bucket(bucket_name, "Prod/audi_ag/email_json/", 's3_data/email_json')