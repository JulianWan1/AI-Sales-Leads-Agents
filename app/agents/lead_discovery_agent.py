import json

from app.services.openai_service import client

import time

from app.services.logger import logger


def generate_leads(context):

    start_time = time.time()

    logger.info("Starting lead discovery agent")

    prompt = f"""
    You are a sales lead generation AI.

    Generate 5 high-quality potential sales leads.

    Business Industry:
    {context['industry']}

    Ideal Customer:
    {context['ideal_customer']}

    Product:
    {context['product']}

    Return ONLY valid JSON.

    Example format:
    [
      {{
        "company": "Example Company",
        "contact": "John Tan",
        "role": "Founder",
        "interest": "Track events",
        "budget_signal": "High"
      }}
    ]
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    content = response.choices[0].message.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")

    execution_time = round(time.time() - start_time, 2)

    logger.info(f"Lead discovery completed in {execution_time}s")

    return json.loads(content)
