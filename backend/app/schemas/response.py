from pydantic import BaseModel
from utils.constants import METADATA_TAGS_MEDDPICC
from typing import List


class SubQuestion(BaseModel):
    question: str
    tags: List[METADATA_TAGS_MEDDPICC]


class QueryRequest(BaseModel):
    query: str
    company: str
    company: str
    sub_questions: List[SubQuestion]


class QueryResponse(BaseModel):
    response: str
    email_contributions: List[dict]
    email_contributions_attachments: List[dict]


class CompaniesResponse(BaseModel):
    id: int
    company_name: str


class CompanyResponse(BaseModel):
    id: int
    company_name: str
    company_email_table: str
    company_attachments_table: str
    s3_prefix: str

    class Config:
        from_attributes = True
