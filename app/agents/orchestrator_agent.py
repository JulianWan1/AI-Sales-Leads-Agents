import time

from app.services.logger import logger
from app.agents.lead_enrichment_agent import _enrich_single_lead
from app.agents.lead_scoring_agent import _score_single_lead
from app.agents.outreach_strategy_agent import _generate_single_outreach


def _is_fallback(lead_state):
    return (
        lead_state.get("research_confidence") == "low"
        and lead_state.get("contact") == "N/A"
        and lead_state.get("company_summary") == "Insufficient company information available."
        and lead_state.get("qualification_signals") == ["No research data available"]
    )


def _orchestrate_single_lead(context, company_name):
    logger.info(f"Orchestrating lead: {company_name}")

    lead_state = {"company": company_name}

    result = _enrich_single_lead(context, lead_state.copy())
    lead_state.update(result)

    if _is_fallback(lead_state):
        logger.info(f"Lead dropped [{company_name}]: Enrichment returned no useful information")
        return None

    result = _score_single_lead(context, lead_state.copy())
    lead_state.update(result)

    if lead_state.get("lead_score", 0) >= 40 and lead_state.get("research_confidence") == "low":
        logger.info(f"Re-enriching lead [{company_name}]: score={lead_state['lead_score']}, confidence=low")
        result = _enrich_single_lead(context, {"company": company_name})
        lead_state.update(result)
        result = _score_single_lead(context, lead_state.copy())
        lead_state.update(result)

    result = _generate_single_outreach(context, lead_state.copy())
    lead_state.update(result)

    logger.info(
        f"Lead complete [{company_name}]: "
        f"score={lead_state.get('lead_score')}, priority={lead_state.get('priority')}"
    )
    return lead_state


def orchestrate_pipeline(context, discovered_leads):

    start_time = time.time()
    logger.info("Starting orchestrator agent")

    results = []
    dropped = 0
    for lead in discovered_leads:
        result = _orchestrate_single_lead(context, lead["company"])
        if result:
            results.append(result)
        else:
            dropped += 1

    results = sorted(results, key=lambda x: x.get("lead_score", 0), reverse=True)

    execution_time = round(time.time() - start_time, 2)
    logger.info(
        f"Orchestrator completed in {execution_time}s — "
        f"{len(results)}/{len(discovered_leads)} leads processed, {dropped} dropped"
    )

    return {"leads": results, "dropped": dropped}
