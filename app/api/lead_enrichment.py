from fastapi import APIRouter

from app.services.context_store import business_context_memory
from app.agents.lead_discovery_agent import generate_leads
from app.agents.lead_enrichment_agent import enrich_leads

router = APIRouter()


@router.post("/enrich-leads")
def enrich_lead_pipeline():

    context = business_context_memory.get("context")

    if not context:
        return {"error": "Business context not found"}

    discovered_leads = generate_leads(context)

    enriched_leads = enrich_leads(context, discovered_leads)

    return {"total_leads": len(enriched_leads), "enriched_leads": enriched_leads}
