import json

from app.services.openai_service import client

import time

from app.services.logger import logger
from app.utils.context_serializer import serialize_business_context


def enrich_leads(context, leads):

    start_time = time.time()

    logger.info("Starting lead enrichment agent")

    prompt = f"""
    You are a sales intelligence AI.

    Given the business context and lead list below,
		preserve ALL existing lead fields and enrich each lead with:

    - estimated_budget
    - purchase_likelihood
    - qualification_signals
    - recommended_sales_angle

    Business Context:
    {json.dumps(
        serialize_business_context(context),
        indent=2
    )}

    Leads:
    {json.dumps(leads, indent=2)}

    Return ONLY valid JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    content = response.choices[0].message.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")

    execution_time = round(time.time() - start_time, 2)

    logger.info(f"Lead enrichment completed in {execution_time}s")

    return json.loads(content)
