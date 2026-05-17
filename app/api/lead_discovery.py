from fastapi import APIRouter

from app.services.context_store import business_context_memory
from app.agents.lead_discovery_agent import generate_leads

router = APIRouter()


@router.post("/discover-leads")
def discover_leads():

    context = business_context_memory.get("context")

    if not context:
        return {"error": "Business context not found"}

    leads = generate_leads(context)

    return {"total_leads": len(leads), "leads": leads}
