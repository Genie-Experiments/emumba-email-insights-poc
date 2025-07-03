import os
import json
import re

from .email_processing import extract_main_email_body, process_email, process_threads
from .graph_api import get_email_by_id, get_emails, get_token
from .s3_utils import upload_to_s3
from .utils import generate_custom_uuid_with_timestamp
from email_ingestion.config.OutlookConfig import outlook_config
import shutil

all_emails = []


def outlook_main(emails, attachments_dir, email_dir, search_query):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # email_dir = outlook_config.email_dir
    # attachments_dir = outlook_config.attachments_dir

    print(f"Email Directory: {email_dir}")
    print(f"Attachments Directory: {attachments_dir}")

    os.makedirs(email_dir, exist_ok=True)
    os.makedirs(attachments_dir, exist_ok=True)

    all_email_ids = emails
    processed_conversation_ids = set()
    json_file_count = 0

    for email_id in all_email_ids:
        all_emails, email_count = get_emails(
            email_id, headers, search_query=search_query
        )
        print(f"Found {email_count} emails for {email_id}")

        for email in all_emails:
            single_email, received_date, conversation_id, body_content, email_json = (
                process_email(email)
            )

            if conversation_id in processed_conversation_ids:
                print(f"Skipping already processed conversation ID: {conversation_id}")
                continue

            print(f"Processing conversation ID: {conversation_id}")
            processed_conversation_ids.add(conversation_id)

            thread_contents, received_date_time, last_json, attachment_names_all = (
                process_threads(conversation_id, email_id, headers)
            )
            print(f"Received Time: {received_date_time}")

            id = generate_custom_uuid_with_timestamp(received_date_time)
            print(f"Generated custom UUID: {id}")

            email_ids = [email["EmailId"] for email in thread_contents]
            conversation_ids = [email["ConversationId"] for email in thread_contents]

            print(f"Total Email IDs in thread: {len(email_ids)}")

            for i in range(len(email_ids)):
                email, attachment_names = get_email_by_id(
                    email_ids[i], email_id, headers, attachments_dir=attachments_dir
                )
                if email is None:
                    print(f"Skipping email {email_id} due to retrieval error.")
                    continue
                (
                    single_email,
                    received_date,
                    conversation_id,
                    body_content,
                    email_json,
                ) = process_email(email)

                text = extract_main_email_body(body_content)
                cleaned_text = re.sub(r"[^\x00-\x7F]+", " ", text)
                email_json["Body Text"] = cleaned_text
                email_json["AttachmentNames"] = attachment_names

                json_filename = os.path.join(email_dir, f"{email_ids[i]}.json")
                with open(json_filename, "w", encoding="utf-8") as json_file:
                    json.dump(email_json, json_file, ensure_ascii=False, indent=4)
                    json_file_count += 1
                    print(f"Saved email JSON to {json_filename}")

                upload_to_s3(json_filename, f"{email_dir}/{email_ids[i]}.json")
                print(f"Uploaded {json_filename} to S3")

                all_emails_filename = os.path.join(email_dir, "all_emails.json")
                with open(
                    all_emails_filename, "a", encoding="utf-8"
                ) as all_emails_file:
                    json.dump(email_json, all_emails_file, ensure_ascii=False, indent=4)
                    print(f"Saved all email JSONs to {all_emails_filename}")

    print(f"Total JSON files created: {json_file_count}")
    shutil.rmtree(email_dir)
    shutil.rmtree(attachments_dir)
