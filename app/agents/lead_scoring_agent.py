import json

from app.services.openai_service import client

import time

from app.services.logger import logger
from app.utils.context_serializer import serialize_business_context


def score_leads(context, enriched_leads):

    start_time = time.time()

    logger.info("Starting lead scoring agent")

    prompt = f"""
    You are a sales lead scoring AI.

    Based on the business context and enriched leads below,
    preserve ALL existing lead fields and assign each lead:

    - lead_score (0-100)
    Scoring guidance:
        - 80-100 → strong verified lead
        - 60-79 → moderate opportunity
        - 40-59 → weak/incomplete lead
        - below 40 → low confidence or poor fit
    - priority
    - score_reasoning

    IMPORTANT SCORING RULES:

    You MUST score leads STRICTLY based on the provided workflow state.

    Do NOT assume information that is not explicitly present.

    Research confidence should significantly influence:
    - scoring confidence
    - purchase likelihood
    - priority

    Example, if:
    - research_confidence is "low"
    - detected_industry is "Unknown"
    - estimated_budget is 0
    - budget_signal is "None"

    then scoring confidence and lead quality should be reduced accordingly.

    Missing or weak research data MUST negatively impact:
    - lead_score
    - purchase_likelihood
    - priority

    Qualification signals MUST reference ONLY existing lead fields.

    Do NOT invent:
    - budget fit
    - industry alignment
    - buying intent
    - exclusivity indicators

    unless explicitly supported by the workflow state.

    Do NOT describe budget fit or budget signals
    unless:
    - budget_signal is explicitly positive
    OR
    - estimated_budget is meaningfully above zero.

    If evidence is weak or incomplete,
    the scoring should be conservative.

    Business Context:
    {json.dumps(
        serialize_business_context(context),
        indent=2
    )}

    Enriched Leads:
    {json.dumps(enriched_leads, indent=2)}

    Return ONLY valid JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    content = response.choices[0].message.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")

    scored_leads = json.loads(content)

    scored_leads = sorted(scored_leads, key=lambda x: x["lead_score"], reverse=True)

    execution_time = round(time.time() - start_time, 2)

    logger.info(f"Lead scoring completed in {execution_time}s")

    return scored_leads
