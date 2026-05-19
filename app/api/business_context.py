from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.business_context import BusinessContextCreate

from app.services.business_context_service import create_business_context

router = APIRouter()


@router.post("/business-context")
def set_business_context(context: BusinessContextCreate, db: Session = Depends(get_db)):

    saved_context = create_business_context(db, context.model_dump())

    return {
        "message": "Business context stored successfully",
        "context_id": saved_context.id,
    }
