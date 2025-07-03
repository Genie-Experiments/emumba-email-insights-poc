# app/routers/company_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from db.database import get_db
from schemas.response import CompanyResponse, CompaniesResponse
from services.companies_service import (
    get_companies,
    get_company_by_name,
)

companiesRouter = APIRouter()


@companiesRouter.get("/", response_model=List[CompaniesResponse])
def read_companies(db: Session = Depends(get_db)):
    companies = get_companies(db=db)
    return companies


@companiesRouter.get("/{company_name}", response_model=CompanyResponse)
def read_company_by_name(company_name: str, db: Session = Depends(get_db)):
    company = get_company_by_name(db, company_name)
    return company
