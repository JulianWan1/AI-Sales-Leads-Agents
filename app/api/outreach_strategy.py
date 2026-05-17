from fastapi import APIRouter

from app.services.context_store import business_context_memory

from app.agents.lead_discovery_agent import generate_leads
from app.agents.lead_enrichment_agent import enrich_leads
from app.agents.lead_scoring_agent import score_leads
from app.agents.outreach_strategy_agent import generate_outreach_strategies
from app.services.lead_persistence_service import save_leads
from app.services.logger import logger

router = APIRouter()


def clean_final_leads(leads):

    fields_to_remove = ["budget_signal", "priority"]

    cleaned_leads = []

    for lead in leads:

        cleaned_lead = {
            key: value for key, value in lead.items() if key not in fields_to_remove
        }

        cleaned_leads.append(cleaned_lead)

    return cleaned_leads


@router.post("/generate-strategies")
def outreach_strategy_pipeline():

    logger.info("Starting full AI sales pipeline")

    context = business_context_memory.get("context")

    if not context:
        return {"error": "Business context not found"}

    # Step 3 — Lead Discovery
    discovered_leads = generate_leads(context)

    # Step 4 — Lead Enrichment
    enriched_leads = enrich_leads(context, discovered_leads)

    # Step 5 — Lead Scoring
    scored_leads = score_leads(context, enriched_leads)

    # Step 6 — Outreach Strategy
    final_leads = generate_outreach_strategies(context, scored_leads)

    # Remove redundant fields
    final_leads = clean_final_leads(final_leads)

    save_leads(final_leads)

    logger.info(f"Pipeline completed successfully with {len(final_leads)} leads")

    return {
        "business_context": context,
        "total_leads": len(final_leads),
        "final_leads": final_leads,
    }
