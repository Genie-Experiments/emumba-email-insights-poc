import boto3
from botocore.exceptions import NoCredentialsError
from email_ingestion.config.Config import config

s3 = boto3.client(
    "s3",
    endpoint_url=config.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
)
bucket_name = config.AWS_S3_BUCKET


def upload_to_s3(file_path, s3_path):
    try:
        s3.upload_file(file_path, bucket_name, s3_path)
        print(f"Uploaded {file_path} to s3://{bucket_name}/{s3_path}")
    except FileNotFoundError:
        print(f"The file was not found: {file_path}")
    except NoCredentialsError:
        print("Credentials not available")
