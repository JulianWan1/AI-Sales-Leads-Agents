
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.services.business_context_service import get_latest_business_context
from app.agents.lead_discovery_agent import generate_leads

router = APIRouter()


@router.post("/discover-leads")
def discover_leads(db: Session = Depends(get_db)):

    context = context = get_latest_business_context(db)

    if not context:
        return {"error": "Business context not found"}

    leads = generate_leads(context)

    return {"total_leads": len(leads), "leads": leads}
