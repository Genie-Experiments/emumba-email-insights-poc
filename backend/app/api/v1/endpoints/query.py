from fastapi import APIRouter, Depends, HTTPException
from schemas.response import QueryRequest, QueryResponse
from services.rag_service import RAGService
from config.LoggingConfig import logger
import traceback
from db.database import get_db
from sqlalchemy.orm import Session

queryRouter = APIRouter()


@queryRouter.post("/generate", response_model=QueryResponse)
async def generate_rag_response(
    request: QueryRequest,
    rag_service: RAGService = Depends(RAGService),
    db: Session = Depends(get_db),
):
    try:
        (
            final_response,
            email_contributions,
            email_contributions_attachments,
        ) = await rag_service.get_response(
            main_question=request.query,
            company=request.company,
            sub_questions_from_request=request.sub_questions,
            db=db,
        )
        return QueryResponse(
            response=final_response,
            email_contributions=email_contributions,
            email_contributions_attachments=email_contributions_attachments,
        )
    except Exception as e:
        traceback_str = "".join(traceback.format_exception(None, e, e.__traceback__))
        logger.info(f"Error occurred: {traceback_str}")
        raise HTTPException(status_code=500, detail=str(e))
