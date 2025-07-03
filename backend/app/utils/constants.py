from enum import Enum


class METADATA_TAGS_MEDDPICC(Enum):
    METRICS = "metrics"
    ECONOMIC_BUYER = "economic-buyer"
    DECISION_CRITERIA = "decision-criteria"
    DECISION_PROCESS = "decision-process"
    PAPER_PROCESS = "paper-process"
    IDENTIFIED_PAIN = "identified-pain"
    CHAMPION = "champion"
    COMPETITION = "competition"
    OTHER = "other"


class QUESTIONS(Enum):
    Q1 = "What was the customer's overall business goals and strategic direction when we first engaged?"
    Q2 = "What were their identified initial pain points, challenges, and key business initiatives?"
    Q3 = "What was our value proposition that specifically addressed the customer's challenges and aligned with their strategic goals? How did we solve them? What were the use-cases?"
    Q4 = "How did our offering address their needs better than competitors?"
    Q5 = "How exactly was the customer's organization mapped out? Who were the key decision-makers and influencers involved in the buying process along the way?"


class S3_TYPES(Enum):
    EMAIL = "email_json"
    ATTACHMENT = "attachments"


cors_origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]
