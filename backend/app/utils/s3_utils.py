import aioboto3
from config.Config import config
from botocore.exceptions import NoCredentialsError, ClientError
import json
from config.LoggingConfig import logger
import os
from utils.constants import S3_TYPES
from services.companies_service import get_company_by_name
from sqlalchemy.orm import Session

# TODO: Move this to config
aws_region = "us-east-2"


def company_s3_prefix(company, type):
    prefix = f"Prod/{company}/{type}/"
    return prefix


async def get_s3_content(email_ids, company):
    session = aioboto3.Session()
    async with session.client(
            "s3",
            region_name=aws_region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            endpoint_url=config.AWS_S3_ENDPOINT_URL,
    ) as s3:
        type = S3_TYPES.EMAIL.value
        s3_prefix = company_s3_prefix(company=company, type=type)
        s3_contents = {}
        try:
            result = await s3.list_objects_v2(
                Bucket=config.AWS_S3_BUCKET, Prefix=s3_prefix
            )
            if "Contents" not in result:
                logger.info(f"No objects found in the S3 folder '{s3_prefix}'.")
                return s3_contents

            email_ids_set = set(email_ids)
            for email_id in email_ids_set:
                s3_key = f"{s3_prefix}{email_id}.json"
                try:
                    response = await s3.get_object(
                        Bucket=config.AWS_S3_BUCKET, Key=s3_key
                    )
                    content = await response["Body"].read()
                    json_content = json.loads(content.decode("utf-8"))
                    s3_contents[email_id] = json_content

                except ClientError as e:
                    if e.response["Error"]["Code"] == "NoSuchKey":
                        logger.error(f"No object found at key '{s3_key}'.")
                    else:
                        logger.error(f"Error fetching content for {s3_key}: {e}")
            return s3_contents
        except NoCredentialsError:
            logger.error("Credentials not available.")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"Error occurred: {error_code} - {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")


def save_combined_json(s3_contents, output_file):
    combined_content = {"emails": s3_contents}
    with open(output_file, "w") as f:
        json.dump(combined_content, f, indent=2)


def format_emails_from_json(input_file):
    with open(input_file, "r") as f:
        combined_content = json.load(f)
    emails = combined_content.get("emails", {})
    formatted_emails = []
    seen_email_ids = set()
    for email_id, content in emails.items():
        if email_id in seen_email_ids:
            continue

        seen_email_ids.add(email_id)
        to_addresses = [to["emailAddress"]["address"] for to in content.get("To", [])]
        formatted_email = {
            "EmailID": email_id,
            "Subject": content.get("Subject"),
            "From": content.get("From"),
            "To": to_addresses,
            "CC": (
                content.get("CC")
                if isinstance(content.get("CC"), list)
                else [content.get("CC")]
            ),
            "BCC": (
                content.get("BCC")
                if isinstance(content.get("BCC"), list)
                else [content.get("BCC")]
            ),
            "Date": content.get("Received DateTime"),
            "Body": content.get("Body Text"),
            "Attachments": content.get("AttachmentNames"),
        }

        formatted_emails.append(formatted_email)
    return formatted_emails


async def get_email_references(email_ids, company):
    logger.info(f"Getting email references....")
    unique_email_ids = list(set(email_ids))
    output_file = "combined.json"
    s3_content = await get_s3_content(unique_email_ids, company=company)
    save_combined_json(s3_content, output_file)
    formatted_emails = format_emails_from_json(output_file)
    os.remove(output_file)
    logger.info(f"Retrieved {len(formatted_emails)} email references")
    return formatted_emails


async def get_attachments_from_s3(attachment_names, company, db):
    async with aioboto3.Session().client(
            "s3",
            region_name=aws_region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            endpoint_url=config.AWS_S3_ENDPOINT_URL,
    ) as s3:
        company = get_company_by_name(db, company)
        s3_prefix = company_s3_prefix(
            company=company.s3_prefix, type=S3_TYPES.ATTACHMENT.value
        )
        logger.info(f"Getting attachments from S3 for prefix '{s3_prefix}'")
        logger.info(f"Attachment names: {attachment_names}")
        attachment_urls = []
        for attachment_name in attachment_names:
            s3_key = f"{s3_prefix}{attachment_name}"
            logger.info(f"Getting attachment from S3 at key '{s3_key}'")
            try:
                attachment_url = await s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": config.AWS_S3_BUCKET, "Key": s3_key},
                    ExpiresIn=604800,
                )
                logger.info(f"Generated pre-signed URL: '{attachment_url}'")
                attachment_urls.append((attachment_name, attachment_url))

            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logger.error(
                        f"No object found for attachment '{attachment_name}' at key '{s3_key}'."
                    )
                else:
                    logger.error(
                        f"Error generating pre-signed URL for attachment '{attachment_name}': {e}"
                    )
            except Exception as e:
                logger.error(
                    f"An error occurred while generating pre-signed URL for attachment '{attachment_name}': {e}"
                )

        return attachment_urls


async def get_email_text_by_id(email_id, company, db):
    async with aioboto3.Session().client(
            "s3",
            region_name=aws_region,
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            endpoint_url=config.AWS_S3_ENDPOINT_URL,
        ) as s3:
        company = get_company_by_name(db, company)

        s3_prefix = company_s3_prefix(
            company=company.s3_prefix, type=S3_TYPES.EMAIL.value
        )

        try:
            result = await s3.list_objects_v2(
                Bucket=config.AWS_S3_BUCKET, Prefix=s3_prefix
            )
            if "Contents" not in result:
                logger.warning(f"No objects found in the S3 folder '{s3_prefix}'.")
                return None

            if email_id:
                s3_key = f"{s3_prefix}{email_id}.json"
                try:
                    response = await s3.get_object(
                        Bucket=config.AWS_S3_BUCKET, Key=s3_key
                    )
                    content = await response["Body"].read()
                    json_content = json.loads(content.decode("utf-8"))
                    body_content = json_content.get("Body Text", None)

                except ClientError as e:
                    if e.response["Error"]["Code"] == "NoSuchKey":
                        logger.error(
                            f"No object found for email ID '{email_id}' at key '{s3_key}'."
                        )
                    else:
                        logger.warning(f"Error fetching content for {s3_key}: {e}")
                finally:
                    return body_content
        except NoCredentialsError:
            logger.warning("Credentials not available.")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            logger.error(f"Error occurred: {error_code} - {e}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
