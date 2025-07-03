import yaml
import logging

from email_ingestion.outlook_ingestion.outlook_main import outlook_main
from email_ingestion.rds_ingestion.rds import (
    check_company_exists,
    check_s3_folder_status,
    load_company_details_to_rds,
    process_attachments_meddpicc_s3,
    process_emails_meddpicc_s3,
    check_table_row_count,
)
from email_ingestion.utils.failover_utils import handle_failover_cleanup
from email_ingestion.utils.excel_loader import load_excel_file_cleaned, to_snake_case

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def load_config(
    config_file="config.yaml",
):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


def ingest_outlook_to_s3(customers):
    logging.info("Starting Outlook to S3 ingestion")
    for customer in customers:
        target_customer = customer["target_customer"]
        target_emails = customer["target_emails"]

        customer_prefix = to_snake_case(target_customer)
        email_dir = f"Prod/{customer_prefix}/email_json"
        attachments_dir = f"Prod/{customer_prefix}/attachments"

        logging.info(f"Processing {target_customer} for Outlook to S3 ingestion")

        if check_s3_folder_status(email_dir):
            logging.info(f"S3 folder for {target_customer} already exists, skipping...")
            continue

        outlook_main(
            emails=target_emails,
            attachments_dir=attachments_dir,
            email_dir=email_dir,
            search_query=target_customer,
        )
        logging.info(f"Completed Outlook to S3 ingestion for {target_customer}")


def process_emails(customers):
    logging.info("Starting email processing")
    for customer in customers:
        target_customer = customer["target_customer"]
        customer_prefix = to_snake_case(target_customer)
        email_dir = f"Prod/{customer_prefix}/email_json"
        logging.info(f"Processing emails for {target_customer}")
        if check_company_exists(target_customer):
            logging.info(
                f"Company {target_customer} already exists, checking row count..."
            )
            row_count = check_table_row_count(f"data_{customer_prefix}_emails")
            if row_count > 0:
                logging.info(f"Emails for {target_customer} are not 0, Continuing...")
                continue
        else:
            logging.info(f"Loading company details for {target_customer}")
            load_company_details_to_rds(
                customer["target_customer"],
                f"{customer_prefix}_emails",
                f"{customer_prefix}_attachments",
                customer_prefix,
            )
        logging.info(f"Processing Emails for {target_customer}")
        process_emails_meddpicc_s3(
            current_company=customer_prefix,
            s3_emails_folder=email_dir,
            rds_table=f"{customer_prefix}_emails",
        )
        logging.info(f"Completed email processing for {target_customer}")


def process_attachments(customers):
    logging.info("Starting attachment processing")
    for customer in customers:
        target_customer = customer["target_customer"]
        customer_prefix = to_snake_case(target_customer)
        attachments_dir = f"Prod/{customer_prefix}/attachments"
        logging.info(f"Processing attachments for {target_customer}")
        if check_company_exists(target_customer):
            logging.info(
                f"Attachments for {target_customer} already processed, checking row count..."
            )
            row_count = check_table_row_count(f"data_{customer_prefix}_attachments")
            if row_count > 0:
                logging.info(
                    f"Attachments for {target_customer} are not 0, Continuing..."
                )
                continue
            else:
                logging.info(f"Processing Attachments for {target_customer}")
                process_attachments_meddpicc_s3(
                    current_company=customer_prefix,
                    s3_attachments_folder=attachments_dir,
                    rds_table=f"{customer_prefix}_attachments",
                )
                logging.info(f"Completed attachment processing for {target_customer}")
        else:
            logging.info(f"Loading company details for {target_customer}")
            load_company_details_to_rds(
                customer["target_customer"],
                f"{customer_prefix}_emails",
                f"{customer_prefix}_attachments",
                customer_prefix,
            )
            process_attachments_meddpicc_s3(
                current_company=customer_prefix,
                s3_attachments_folder=attachments_dir,
                rds_table=f"{customer_prefix}_attachments",
            )
            logging.info(f"Completed attachment processing for {target_customer}")


def main():
    file_path = "customers.xlsx"
    print(f"File Path: {file_path}")
    handle_failover_cleanup()
    customers = load_excel_file_cleaned(file_path=file_path)
    ingest_outlook_to_s3(customers)
    process_emails(customers)
    process_attachments(customers)


if __name__ == "__main__":
    main()
