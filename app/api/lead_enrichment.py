from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.agents.lead_discovery_agent import generate_leads
from app.agents.lead_enrichment_agent import enrich_leads
from app.services.business_context_service import get_latest_business_context

router = APIRouter()


@router.post("/enrich-leads")
def enrich_lead_pipeline(db: Session = Depends(get_db)):

    context = context = get_latest_business_context(db)

    if not context:
        return {"error": "Business context not found"}

    discovered_leads = generate_leads(context)

    enriched_leads = enrich_leads(context, discovered_leads)

    return {"total_leads": len(enriched_leads), "enriched_leads": enriched_leads}
