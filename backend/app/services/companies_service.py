from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from db.schemas.company import Company


def get_companies(db: Session):
    try:
        companies = db.query(Company).order_by(Company.company_name.asc()).all()
        if not companies:
            raise HTTPException(status_code=404, detail="No companies found")
        return companies
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database query error") from e



def get_company_by_name(db: Session, company_name: str):
    try:
        company = db.query(Company).filter(Company.company_name == company_name).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database query error") from e
