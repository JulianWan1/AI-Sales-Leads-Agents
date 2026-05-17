import json

from app.services.openai_service import client

import time

from app.services.logger import logger


def score_leads(context, enriched_leads):

    start_time = time.time()

    logger.info("Starting lead scoring agent")

    prompt = f"""
    You are a sales lead scoring AI.

    Based on the business context and enriched leads below,
		preserve ALL existing lead fields and assign each lead:

    - lead_score (0-100)
    - priority
    - score_reasoning

    Prioritize:
    - budget fit
    - buying intent
    - industry alignment
    - exclusivity potential

    Business Context:
    {json.dumps(context, indent=2)}

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
