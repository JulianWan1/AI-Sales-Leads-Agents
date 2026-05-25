import json
import time

from app.services.openai_service import client
from app.services.logger import logger
from app.utils.context_serializer import serialize_business_context


SYSTEM_PROMPT = """You are a sales lead scoring AI.

Your task is to score a single lead based on its enrichment data and business context.

## Scoring guidance

- 80–100 → strong verified lead: clear industry fit, strong budget signals, high confidence
- 60–79 → moderate opportunity: good fit indicators but incomplete evidence
- 40–59 → weak or incomplete lead: some signals but significant gaps
- below 40 → low confidence or poor fit

## Output format (return ONLY valid JSON, no markdown):
{
  "lead_score": <integer 0-100>,
  "priority": "High | Medium | Low",
  "score_reasoning": "Concise explanation citing specific evidence from the enrichment data"
}

priority guidance:
- High → lead_score 70+
- Medium → lead_score 40–69
- Low → lead_score below 40

IMPORTANT: Return ONLY these three fields. All other lead fields are preserved separately."""


def _build_user_prompt(context, lead):
    return f"""Score this lead.

Company: {lead["company"]}

Enrichment data:
{json.dumps({k: v for k, v in lead.items() if k != "company"}, indent=2)}

Business context (our product):
{json.dumps(serialize_business_context(context), indent=2)}

Return the scoring JSON."""


def _fallback_score(lead):
    return {
        **lead,
        "lead_score": 0,
        "priority": "Low",
        "score_reasoning": "Scoring failed — no response produced.",
    }


def _score_single_lead(context, lead):
    company_name = lead["company"]
    logger.info(f"Scoring lead: {company_name}")

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(context, lead)},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content
    if not content:
        logger.warning(f"Empty scoring response for {company_name}")
        return _fallback_score(lead)

    content = content.strip().replace("```json", "").replace("```", "")
    score = json.loads(content)
    logger.info(
        f"Scored {company_name}: "
        f"score={score.get('lead_score')}, "
        f"priority={score.get('priority')}"
    )
    return {**lead, **score}


def score_leads(context, enriched_leads):

    start_time = time.time()
    logger.info("Starting lead scoring agent")

    scored = [_score_single_lead(context, lead) for lead in enriched_leads]
    scored = sorted(scored, key=lambda x: x["lead_score"], reverse=True)

    execution_time = round(time.time() - start_time, 2)
    logger.info(f"Lead scoring completed in {execution_time}s")

    return scored
