import json

from app.services.openai_service import client

import time

from app.services.logger import logger


def generate_outreach_strategies(context, scored_leads):

    start_time = time.time()

    logger.info("Starting outreach strategy agent")

    prompt = f"""
    You are an AI sales strategist.

    Based on the business context and scored leads below,
    generate for each lead:

    - outreach_strategy
    - conversation_starter
    - likely_objections
    - recommended_next_action

    IMPORTANT:
    Preserve ALL existing lead fields.

    Business Context:
    {json.dumps(context, indent=2)}

    Scored Leads:
    {json.dumps(scored_leads, indent=2)}

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

    logger.info(f"Outreach strategy completed in {execution_time}s")

    return json.loads(content)
