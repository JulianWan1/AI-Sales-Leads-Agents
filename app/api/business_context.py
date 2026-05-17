from fastapi import APIRouter
from app.models.business_context import BusinessContext
from app.services.context_store import business_context_memory

router = APIRouter()


@router.post("/business-context")
def set_business_context(context: BusinessContext):

    business_context_memory["context"] = context.dict()

    return {
        "message": "Business context stored successfully",
        "context": business_context_memory["context"],
    }
