import os
import json
import boto3
import psycopg2
import tiktoken

from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.embeddings.text_embeddings_inference import (
    TextEmbeddingsInference,
)
from llama_index.core import (
    VectorStoreIndex,
    Settings,
    StorageContext,
    SimpleDirectoryReader,
)
from llama_index.core.node_parser import (
    SemanticSplitterNodeParser,
    SimpleFileNodeParser
)
from botocore.exceptions import NoCredentialsError, ClientError
from llama_index.readers.s3 import S3Reader

# local imports
import logging
from email_ingestion.config.VectorStore import VectorStoreSingleton
from email_ingestion.rds_ingestion.generate_tags import (
    generate_meddpicc_tags_for_chunks,
)
from email_ingestion.config.Config import config
from email_ingestion.utils.excel_loader import to_snake_case

from llama_index.embeddings.openai import OpenAIEmbedding


AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
AWS_S3_BUCKET = config.AWS_S3_BUCKET
AWS_S3_ENDPOINT_URL = config.AWS_S3_ENDPOINT_URL

embed_model = OpenAIEmbedding(api_key=config.API_KEY, model_name=config.EMBEDDING_MODEL)


s3 = boto3.client("s3", endpoint_url=config.AWS_S3_ENDPOINT_URL)

conn = psycopg2.connect(
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
    database=config.DB_NAME,
)
tags_list_meddpicc = [
    "metrics",
    "economic-buyer",
    "decision-criteria",
    "decision-process",
    "paper-process",
    "identified-pain",
    "champion",
    "competition",
]


def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# function for creating embeddings and storing them in RDS
def load_to_rds(chunks, table_name):
    print('laod_to_rds', table_name)
    Settings.embed_model = embed_model
    Settings.llm = OpenAI(
        base_url=config.LLM_URL,
        model=config.LLM_MODEL,
        api_key=config.API_KEY
    )

    with conn.cursor() as c:
        vector_store = VectorStoreSingleton.get_instance(db_table=table_name)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        print("Creating Index ....")
        VectorStoreIndex(chunks, storage_context=storage_context, show_progress=True)
        conn.commit()


def get_email_of_attachment(s3_email_folder, attachment_name):

    all_emails = get_all_file_keys_from_s3(s3_email_folder)

    # ---------------------------------- FIND THE EMAIL THAT CONTAINS THE ATTACHMENT ---------------------------------- #

    required_email_json = None
    attachments_list = None

    for obj in enumerate(all_emails):
        # logging.info(f"Working with file {obj}")
        s3_key = obj[1]["Key"]

        # Skip directories
        if s3_key.endswith("/"):
            continue

        loader = S3Reader(
            bucket=AWS_S3_BUCKET,
            key=s3_key,
            aws_access_id=AWS_ACCESS_KEY_ID,
            aws_access_secret=AWS_SECRET_ACCESS_KEY,
            endpoint_url=AWS_S3_ENDPOINT_URL
        )

        data = json.loads((loader.load_data())[0].text)

        attachments = data.get("AttachmentNames")
        attachments_list = attachments
        if attachments:
            if attachment_name in attachments:
                required_email_json = data

    return required_email_json, attachments_list


def process_attachments_meddpicc_s3(
    current_company, s3_attachments_folder="", rds_table=""
):
    # Set up logging
    logging.basicConfig(
        filename=f"{current_company}_logs_attachments.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    logging.info(
        "-------------------------------------------------------------------------------------------"
    )
    total_chunks = []
    tags_being_assigned = []
    total_attachments_pushed_to_rds = []
    chunks_with_wrong_tags = []
    unique_email_ids = []
    attachments_with_no_email_reference = []
    attachments_with_no_text = []
    try:
        all_attachments_keys = get_all_file_keys_from_s3(s3_attachments_folder)
        if not all_attachments_keys:
            logging.info(f"No attachments found in S3 folder: {s3_attachments_folder}")
            return
    except Exception as e:
        logging.error(
            f"Error occurred while accessing S3 folder {s3_attachments_folder}: {e}"
        )
        return

    for index, attachment_key in enumerate(all_attachments_keys, start=1):
        logging.info(
            f"Working with file [{attachment_key['Key']}]. . . . .  {index}/{len(all_attachments_keys)}"
        )
        attachment_key = attachment_key["Key"]
        attachment_name = attachment_key.split("/")[-1]
        if attachment_name.endswith((".pdf", ".docx", ".PDF", ".DOCX", ".pptx", ".PPTX")):
            try:
                s3.download_file(AWS_S3_BUCKET, attachment_key, attachment_name)
                docs = SimpleDirectoryReader(input_files=[attachment_name]).load_data()
                os.remove(attachment_name)
                for docu in docs:
                    if docu.text == "":
                        logging.info("No text. Skipping...")
                        attachments_with_no_text.append(attachment_name)
                        continue
                    logging.info(
                        f"Total tokens in the text chunk: {count_tokens(docu.text)}"
                    )
                    # TODO: this code can be moved to a fucn and can be called here and in process_emails_meddpicc_s3
                    text_splits = split_text_according_to_token_limit(docu.text, 500)
                    for text in text_splits:
                        # creating Document
                        doc = Document(
                            text=text, metadata={"AttachmentName": attachment_name}
                        )
                        # creating chunks
                        logging.info("Creating Chunks ....")
                        chunks = create_chunks(doc)
                        total_chunks.extend(chunks)
                        logging.info("Assigning tags ....")
                        for chunk in chunks:
                            tags = generate_meddpicc_tags_for_chunks(chunk.text)
                            # this can be done in a func to make this code clean
                            if len(tags) > 1:
                                for tag in tags:
                                    if tag not in tags_list_meddpicc:
                                        tags.remove(tag)
                            elif len(tags) == 1 and tags[0] not in tags_list_meddpicc:
                                tags = ["other"]
                            chunk.metadata["tags"] = tags
                            tags_being_assigned.extend(tags)
                            for tag in tags:
                                if tag not in tags_list_meddpicc:
                                    chunks_with_wrong_tags.append(chunk)
                        logging.info("Creating Embeddings and loading to rds....")
                        load_to_rds(chunks, f"{rds_table}")
                        total_attachments_pushed_to_rds.append(attachment_name)
            except Exception as e:
                logging.error(
                    f"Error occurred while processing file {attachment_name} ..."
                )
                logging.error(f"Error: {e}")
        else:
            logging.info(f"Skipping file {attachment_name} ...")
    logging.info(f"Tags assigned: {set(tags_being_assigned)}\n")
    logging.info(f"Chunks created: {len(total_chunks)}\n")
    logging.info(f"Unique Email IDs:  {len(set(unique_email_ids))}")
    if unique_email_ids:
        for email_id in unique_email_ids:
            logging.info(email_id)
    logging.info(
        f"Total Attachments pushed to RDS:  {len(total_attachments_pushed_to_rds)}"
    )
    logging.info(f"Chunks with wrong tags:   {len(chunks_with_wrong_tags)}")
    if chunks_with_wrong_tags:
        for chunk in chunks_with_wrong_tags:
            logging.info(chunk.text)
            logging.info(chunk.metadata)
    logging.info(
        f"Attachments with no email reference: {len(attachments_with_no_email_reference)}"
    )
    if attachments_with_no_email_reference:
        for attachment in attachments_with_no_email_reference:
            logging.info(attachment)
    logging.info(
        "-------------------------------------------------------------------------------------------"
    )
    return


def create_chunks(doc):
    splitter = SemanticSplitterNodeParser(
        buffer_size=2,
        breakpoint_percentile_threshold=95,
        embed_model=embed_model,
        include_metadata=True,
        include_prev_next_rel=True,
    )
    chunks = splitter.get_nodes_from_documents([doc], show_progress=True)
    return chunks


def get_all_file_keys_from_s3(s3_folder):

    logging.info("***    Fetching files from S3    ***")

    s3 = boto3.client("s3", endpoint_url=config.AWS_S3_ENDPOINT_URL)
    all_docs = []

    try:
        continuation_token = None
        while True:
            if continuation_token:
                result = s3.list_objects_v2(
                    Bucket=AWS_S3_BUCKET,
                    Prefix=s3_folder,
                    ContinuationToken=continuation_token,
                )
            else:
                result = s3.list_objects_v2(Bucket=AWS_S3_BUCKET, Prefix=s3_folder)

            if "Contents" not in result:
                logging.info(f"'{s3_folder}' Folder doesnt exist or is empty.")
                return

            all_docs.extend(result["Contents"])
            if result.get("IsTruncated"):
                continuation_token = result.get("NextContinuationToken")
            else:
                break

        logging.info("Fetch completed.")

    except NoCredentialsError:
        logging.error("Credentials not found")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        logging.error(f"Error occurred: {error_code} - {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    logging.info(f"Total files:  {len(all_docs)}")

    return all_docs


def load_company_details_to_rds(
    company_name, company_name_emails, company_name_attachments, s3_prefix
):
    with conn.cursor() as c:
        company_name = company_name.replace("'", "")  # Remove apostrophes
        c.execute("SELECT * FROM company_info WHERE company_name = %s", (company_name,))
        if c.fetchone() is None:
            c.execute(
                f"INSERT INTO company_info (company_name, company_email_table, company_attachments_table, s3_prefix ) VALUES ('{company_name}', '{company_name_emails}', '{company_name_attachments}', '{s3_prefix}')"
            )
            conn.commit()
            logging.info(f"Company details inserted into RDS.")
        else:
            logging.info("Company details already present in RDS.")
            conn.commit()


def check_s3_folder_status(folder_name):
    s3 = boto3.client("s3", endpoint_url=config.AWS_S3_ENDPOINT_URL)
    response = s3.list_objects_v2(Bucket=AWS_S3_BUCKET, Prefix=folder_name)
    if "Contents" in response:
        for obj in response["Contents"]:
            if obj["Key"].endswith(".json"):
                return True
    return False


def check_company_exists(company_name):
    try:
        with conn.cursor() as c:
            company_name = company_name.replace("'", "")  # Remove apostrophes
            c.execute("SELECT * FROM company_info WHERE company_name = %s", (company_name,))    
            if c.fetchone() is None:
                logging.info(f"Company '{company_name}' does not exist in RDS.")
                return False
            else:
                logging.info(f"Company '{company_name}' already exists in RDS.")
                return True

    except psycopg2.Error as e:
        logging.error(f"Database error occurred: {e}")
        conn.rollback()  
        return False


def split_text_according_to_token_limit(text, max_tokens):

    if count_tokens(text) < max_tokens:
        return [text]

    half = len(text) // 2
    left = text[0:half]
    right = text[half:]

    return split_text_according_to_token_limit(
        left, max_tokens
    ) + split_text_according_to_token_limit(right, max_tokens)


def check_table_row_count(table_name):
    try:
        with conn.cursor() as c:
            c.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = c.fetchone()[0]
            return row_count
    except Exception as e:
        logging.error(f"Error checking row count for table {table_name}: {e}")
        return 0


def drop_table(table_name):
    try:
        with conn.cursor() as c:
            c.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
            logging.info(f"Table {table_name} dropped.")
    except Exception as e:
        logging.error(f"Error dropping table {table_name}: {e}")
    finally:
        conn.close()


def process_emails_meddpicc_s3(current_company="", s3_emails_folder="", rds_table=""):

    # Set up logging
    logging.basicConfig(
        filename=f"{current_company}_logs.txt",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    logging.info(
        "-------------------------------------------------------------------------------------------"
    )
    logging.info(f"Fetching emails from S3 folder: {s3_emails_folder}")
    try:
        files_with_empty_content = []
        total_chunks = []
        tags_being_assigned = []
        all_docs = []
        logging.info("Fetching files from S3 .....")

        all_docs = get_all_file_keys_from_s3(s3_emails_folder)
        if not all_docs:
            logging.info(f"No emails found in S3 folder: {s3_emails_folder}")
            return
    except Exception as e:
        logging.error(
            f"Error occurred while accessing S3 folder {s3_emails_folder}: {e}"
        )
        return
    

    for file_num, obj in enumerate(all_docs, start=1):
        try:
            s3_key = obj["Key"]

            logging.info(
                f"Working with file {s3_key} {file_num}/{len(all_docs)}. . . . ."
            )

            # Skip directories
            if s3_key.endswith("/"):
                continue

            loader = S3Reader(
                bucket=AWS_S3_BUCKET,
                key=s3_key,
                aws_access_id=AWS_ACCESS_KEY_ID,
                aws_access_secret=AWS_SECRET_ACCESS_KEY,
                s3_endpoint_url=AWS_S3_ENDPOINT_URL
            )

            data = json.loads((loader.load_data())[0].text)

            if data.get("Body Text") == "":
                logging.info("No text. Skipping...")
                files_with_empty_content.append(s3_key)
                continue

            email_text = data.get("Body Text")
            logging.info(f"Total tokens in email: {count_tokens(email_text)}")
            text_splits = split_text_according_to_token_limit(email_text, 500)

            for text in text_splits:
                # creating Document
                doc = Document(
                    text=text,
                    metadata={
                        "EmailID": data.get("EmailID"),
                        "conversation_id": data.get("ConversationId"),
                        "subject": data.get("Subject"),
                        "Received DateTime": data.get("Received DateTime"),
                        "Sent DateTime": data.get("Sent DateTime"),
                        "From": data.get("From"),
                        "CC": data.get("CC"),
                        "BCC": data.get("BCC"),
                        "AttachmentNames": data.get("AttachmentNames"),
                    },
                )

                # creating chunks
                logging.info("Creating Chunks ....")
                chunks = create_chunks(doc)
                total_chunks.extend(chunks)

                # assign tags
                logging.info("Assigning tags ....")
                for chunk in chunks:
                    tags = generate_meddpicc_tags_for_chunks(chunk.text)

                    # remove irrelevant tags if assigned tags are more than 1 and they contain irrelevant tags
                    if len(tags) > 1:
                        for tag in tags:
                            if tag not in tags_list_meddpicc:
                                tags.remove(tag)

                    # assign 'other' if there is only 1 tag generated and it is not present in the meddpicc tags list
                    elif len(tags) == 1 and tags[0] not in tags_list_meddpicc:
                        tags = ["other"]

                    chunk.metadata["tags"] = ",".join(tags)
                    tags_being_assigned.extend(tags)

                # load to rds
                load_to_rds(chunks, table_name=f"{rds_table}")

        except Exception as e:
            logging.error(f"Error occurred.\n {e}")

    logging.info(
        "-------------------------------------------------------------------------------------------"
    )