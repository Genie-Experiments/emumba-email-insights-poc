import psycopg2
from email_ingestion.config.Config import config
from email_ingestion.config.OutlookConfig import outlook_config
import boto3
from email_ingestion.utils.excel_loader import to_snake_case
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def delete_s3_folder(bucket_name, folder_path):
    """
    Delete all objects (files and subfolders) under a specified folder in an S3 bucket.

    :param bucket_name: The name of the S3 bucket
    :param folder_path: The path of the folder to delete (include trailing '/')
    """
    s3 = boto3.client("s3", endpoint_url=config.AWS_S3_ENDPOINT_URL)
    paginator = s3.get_paginator("list_objects_v2")

    if not folder_path.endswith("/"):
        folder_path += "/"

    pages = paginator.paginate(Bucket=bucket_name, Prefix=folder_path)

    delete_list = []

    for page in pages:
        if "Contents" in page:
            for obj in page["Contents"]:
                delete_list.append({"Key": obj["Key"]})

    if delete_list:
        while delete_list:
            s3.delete_objects(
                Bucket=bucket_name, Delete={"Objects": delete_list[:1000]}
            )
            delete_list = delete_list[1000:]
        logging.info(
            f"All objects under '{folder_path}' in bucket '{bucket_name}' deleted successfully."
        )
    else:
        logging.warning(
            f"No objects found under '{folder_path}' in bucket '{bucket_name}'."
        )


def delete_email_table(customer_name, conn):
    table_name = f"data_{customer_name}_emails"
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            conn.commit()
            logging.info(f"Email table '{table_name}' deleted successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error deleting email table '{table_name}': {e}")


def delete_attachment_table(customer_name, conn):
    table_name = f"data_{customer_name}_attachments"
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            conn.commit()
            logging.info(f"Attachment table '{table_name}' deleted successfully.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error deleting attachment table '{table_name}': {e}")


def handle_failover_cleanup():
    try:
        conn = psycopg2.connect(
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
        )
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        return None

    if outlook_config.failover:
        failover_type = outlook_config.failover.get("type")
        customer_name = outlook_config.failover.get("customer")

        if not customer_name:
            logging.warning("Failover config is missing 'customer' information.")
            return
        customer_prefix = to_snake_case(customer_name)
        if failover_type.lower() == "s3":
            delete_s3_folder(
                bucket_name=config.AWS_S3_BUCKET, folder_path=f"Prod/{customer_prefix}"
            )
        elif failover_type.lower() == "email":
            if conn:
                delete_email_table(customer_name=customer_prefix, conn=conn)
            else:
                logging.info("Database connection not provided for email failover.")
        elif failover_type.lower() == "attachment":
            delete_attachment_table(customer_name=customer_prefix, conn=conn)
        else:
            logging.warning(f"Unknown failover type: {failover_type}")
    else:
        logging.error("No failover configuration present in OutlookConfig.")

    if conn:
        conn.close()
        logging.info("Database connection closed.")
