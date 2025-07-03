from dotenv import load_dotenv
import os

load_dotenv()


class config:
    LLM_URL = os.getenv("OPENAI_API_BASE")
    LLM_MODEL = os.getenv("LLM_MODEL")
    API_KEY = os.getenv("API_KEY")
    EMBEDDING_MODEL_URL = os.getenv("EMBEDDING_URL")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
    EMBEDDING_DIM = os.getenv("EMBEDDING_DIM")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")


# init configs
config()
