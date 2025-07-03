import os
import requests
from requests.exceptions import HTTPError
import time
import urllib.parse
from .utils import sanitize_file_name
import boto3
import yaml
from email_ingestion.config.Config import config
from email_ingestion.config.OutlookConfig import outlook_config

s3 = boto3.client(
    "s3",
    endpoint_url=config.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
)

emails = []


def load_config(config_file="config.yaml"):
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config


config = load_config()


def get_token():
    tenant_id = outlook_config.tenant_id
    client_id = outlook_config.client_id
    client_secret = outlook_config.client_secret
    scope = outlook_config.scope

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": " ".join(scope),
    }

    token_r = requests.post(token_url, data=token_data)

    token = token_r.json().get("access_token")

    return token


def get_emails_from_folder(email_id, headers, folder, search_query):
    search_query = search_query
    email_count = 0
    email_ids = set()
    emails = []

    search_query = f'"{search_query}"'
    search_query_encoded = urllib.parse.quote(search_query)
    endpoint = f"https://graph.microsoft.com/v1.0/users/{email_id}/mailFolders/{folder}/messages?$search={search_query_encoded}&top=250"

    while endpoint:
        print(f"Fetching from: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers)

            response.raise_for_status()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 5))
                print(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                continue
            else:
                print(f"HTTP error occurred: {http_err}")
                break
        except Exception as err:
            print(f"An error occurred: {err}")
            break

        data = response.json()

        emails_found = data.get("value", [])
        for email in emails_found:
            email_ids.add(email["id"])
        # print(f"{folder.capitalize()} Email Count: {len(email_ids)}")
        emails.extend(emails_found)
        email_count += len(emails_found)

        endpoint = data.get("@odata.nextLink")
        count = data.get("@odata.count")
        print(f"Total count: {count}")
        if not endpoint:
            break

    return emails, email_count


def get_inbox_emails(email_id, headers, search_query):
    return get_emails_from_folder(email_id, headers, "inbox", search_query)


def get_sent_items_emails(email_id, headers, search_query):
    return get_emails_from_folder(email_id, headers, "sentItems", search_query)


def get_emails(email_id, headers, search_query):
    inbox_emails, inbox_count = get_inbox_emails(email_id, headers, search_query)
    sent_items_emails, sent_items_count = get_sent_items_emails(
        email_id, headers, search_query=search_query
    )

    all_emails = inbox_emails + sent_items_emails
    total_count = inbox_count + sent_items_count

    print(f"Total Email Count: {total_count}")

    return all_emails, total_count


def get_email_by_id(email_id, user_id, headers, attachments_dir):

    try:
        message_endpoint = (
            f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{email_id}"
        )
        response = requests.get(message_endpoint, headers=headers)

        if response.status_code == 404:
            print(f"Message with ID {email_id} not found for user {user_id}.")
            return None
        elif response.status_code != 200:
            print(
                f"Failed to retrieve message for user {user_id}. Status code: {response.status_code}"
            )
            print(f"Response: {response.json()}")
            return None

        message_data = response.json()

        has_attachments = message_data.get("hasAttachments", False)
        processed_attachment_names = []

        if has_attachments:
            print(f"Message with ID {email_id} has attachments.")
            attachments_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{email_id}/attachments"
            attachments_response = requests.get(attachments_endpoint, headers=headers)
            attachments_response.raise_for_status()
            attachments_data = attachments_response.json()

            valid_extensions = {".pdf", ".ppt", ".pptx", ".doc", ".docx"}

            for attachment in attachments_data.get("value", []):
                attachment_id = attachment["id"]
                attachment_name = attachment["name"]

                if not any(
                    attachment_name.lower().endswith(ext) for ext in valid_extensions
                ):
                    continue

                short_attachment_name = sanitize_file_name(attachment_name)
                attachment_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages/{email_id}/attachments/{attachment_id}/$value"

                try:
                    print(f"Getting attachment: {attachment_url}")
                    attachment_response = requests.get(attachment_url, headers=headers)
                    attachment_response.raise_for_status()
                except HTTPError as http_err:
                    print(
                        f"HTTP error occurred while downloading {short_attachment_name}: {http_err}"
                    )
                    continue
                except Exception as err:
                    print(
                        f"An error occurred while downloading {short_attachment_name}: {err}"
                    )
                    continue

                attachment_path = os.path.join(attachments_dir, short_attachment_name)
                os.makedirs(os.path.dirname(attachment_path), exist_ok=True)

                with open(attachment_path, "wb") as file:
                    file.write(attachment_response.content)
                print(f"Attachments directory {attachments_dir}")
                s3_key = f"{attachments_dir}/{short_attachment_name}"
                s3.upload_file(attachment_path, "emumba-outlook-ingestion", s3_key)

                os.remove(attachment_path)
                processed_attachment_names.append(short_attachment_name)

            return message_data, processed_attachment_names
        else:
            print(f"Message with ID {email_id} does not have attachments.")
            return message_data, []

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while trying to retrieve the message: {str(e)}")
        return None, []
