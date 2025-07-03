from sqlalchemy import Column, Integer, String
from db.database import Base


class Company(Base):
    __tablename__ = "company_info"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=False)
    company_email_table = Column(String, nullable=False)
    company_attachments_table = Column(String, nullable=False)
    s3_prefix = Column(String, nullable=False)
