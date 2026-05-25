import re
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.services.logger import logger
from app.agents.lead_discovery_agent import generate_leads
from app.agents.orchestrator_agent import orchestrate_pipeline
from app.services.lead_persistence_service import save_leads
from app.services.business_context_service import get_latest_business_context

router = APIRouter()


def clean_final_leads(leads):

    cleaned_leads = []

    for lead in leads:

        budget = lead.get("estimated_budget")

        if isinstance(budget, str):

            cleaned_budget = re.sub(r"[^\d]", "", budget)

            lead["estimated_budget"] = int(cleaned_budget) if cleaned_budget else 0

        cleaned_leads.append(lead)

    return cleaned_leads


@router.post("/generate-strategies")
def outreach_strategy_pipeline(db: Session = Depends(get_db)):

    logger.info("Starting full AI sales pipeline")

    context = context = get_latest_business_context(db)

    if not context:
        return {"error": "Business context not found"}

    # Step 3 — Lead Discovery
    discovered_leads = generate_leads(context)

    # Step 4 — Orchestrate: enrich, score, re-enrich if needed, outreach (per lead)
    final_leads = orchestrate_pipeline(context, discovered_leads)

    # Remove redundant fields
    final_leads = clean_final_leads(final_leads)

    save_leads(db, final_leads)

    logger.info(f"Pipeline completed successfully with {len(final_leads)} leads")

    return {
        "business_context": context,
        "total_leads": len(final_leads),
        "final_leads": final_leads,
    }
