from typing import Optional
from utils.constants import (
    QUESTIONS,
)
from sqlalchemy.orm import Session
from services.companies_service import get_company_by_name


def get_db_table(company: str, db: Session) -> Optional[str]:
    """
    Returns the database table name corresponding to the given company.

    Args:
        company (Companies): The company enum value.

    Returns:
        Optional[str]: The database table name if the company is valid, otherwise None.
    """
    tables = get_company_by_name(db, company_name=company)
    attachment_table = tables.company_attachments_table
    email_table = tables.company_email_table
    s3_prefix = tables.s3_prefix if tables.s3_prefix else ""
    return email_table, attachment_table, s3_prefix


def filter_nodes(nodes, filter_tags):
    filtered_nodes = []
    filter_tags_set = {tag for tag in filter_tags}
    for node_with_score in nodes:
        node = node_with_score.node
        tags = node.metadata.get("tags", "")
        if isinstance(tags, str):
            tags = tags.split(",")
        if any(tag in filter_tags_set for tag in tags):
            filtered_nodes.append(node_with_score)

    return filtered_nodes


def get_top_k(question):
    top_k = 20
    if question == QUESTIONS.Q1.value:
        top_k = 30
    elif question == QUESTIONS.Q3.value:
        top_k = 12
    return top_k
