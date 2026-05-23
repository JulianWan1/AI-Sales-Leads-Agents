import json
import time

from app.services.openai_service import client
from app.services.logger import logger
from app.utils.context_serializer import serialize_business_context
from app.tools.web_search_tool import search_company


MAX_TOOL_ITERATIONS = 4

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_company",
            "description": (
                "Search for recent information about a company to supplement incomplete "
                "enrichment data before scoring. Use targeted focus terms such as "
                "'recent funding', 'growth news', 'expansion', or 'financial results'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {"type": "string"},
                    "focus": {
                        "type": "string",
                        "description": "Targeted search terms to find relevant signals",
                    },
                },
                "required": ["company_name"],
            },
        },
    }
]

SYSTEM_PROMPT = """You are a sales lead scoring AI.

Your task is to score a single lead based on its enrichment data and business context.

You have one tool:
- search_company: search for recent company news to supplement incomplete enrichment data

## Decision rule — use EXACTLY one of these three branches:

**Branch 1 — Score directly from enrichment data:**
Use this when `research_confidence` is "high". Enrichment was complete; no search needed.

**Branch 2 — Call search_company, then score:**
Use this when `research_confidence` is "low" or "medium" AND at least TWO of the following
positive signals are present in the enrichment data:
- `detected_industry` is not "Unknown" and is relevant to the target industry
- `interest` is not "Unable to determine" and mentions goals aligned with the product
- `budget_signal` is not "None"
- `specialization` is not "Unknown" and suggests product fit
- `purchase_likelihood` is "Medium" or "High"

When calling the tool, use a targeted focus (e.g. "recent funding", "expansion news").

If the search returns meaningful information, treat `research_confidence` as upgraded
(low → medium, medium → high) when applying the scoring guidance. Also, score based on the
totality of evidence now available — enrichment data plus the meaningful information from search results — not the
pre-search confidence label.

**Branch 3 — Score directly but conservatively:**
Use this when `research_confidence` is "low" or "medium" AND fewer than two positive signals
are present. Enrichment was incomplete and there is nothing meaningful to verify; score low.

## Scoring guidance

- 80–100 → strong verified lead: clear industry fit, strong budget signals, high confidence
- 60–79 → moderate opportunity: good fit indicators but incomplete evidence
- 40–59 → weak or incomplete lead: some signals but significant gaps
- below 40 → low confidence or poor fit

## Output format (return ONLY valid JSON, no markdown):
{
  "lead_score": <integer 0-100>,
  "priority": "High | Medium | Low",
  "score_reasoning": "Concise explanation citing specific evidence from the enrichment data",
  "research_confidence": "upgraded value — include ONLY if you took Branch 2 AND the search returned meaningful information. Upgrade by one level: low → medium, medium → high. Omit this field entirely in all other cases."
}

priority guidance:
- High → lead_score 70+
- Medium → lead_score 40–69
- Low → lead_score below 40

IMPORTANT: Return ONLY the fields listed above. Omit `research_confidence` unless Branch 2 was taken and the search was informative. All other lead fields are preserved separately."""


def _build_user_prompt(context, lead):
    return f"""Score this lead.

Company: {lead["company"]}

Enrichment data:
{json.dumps({k: v for k, v in lead.items() if k != "company"}, indent=2)}

Business context (our product):
{json.dumps(serialize_business_context(context), indent=2)}

Apply the decision rule from your instructions, then return the scoring JSON."""


def _dispatch_tool(tool_call):
    args = json.loads(tool_call.function.arguments)
    return search_company(
        company_name=args["company_name"],
        focus=args.get("focus", ""),
    )


def _fallback_score(lead):
    return {
        **lead,
        "lead_score": 0,
        "priority": "Low",
        "score_reasoning": "Scoring failed — max iterations reached without a final score.",
    }


def _score_single_lead(context, lead):
    company_name = lead["company"]
    logger.info(f"Scoring lead: {company_name}")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(context, lead)},
    ]

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
        )

        msg = response.choices[0].message
        messages.append(msg)

        if response.choices[0].finish_reason == "stop":
            content = msg.content.strip().replace("```json", "").replace("```", "")
            score = json.loads(content)
            logger.info(
                f"Scored {company_name}: "
                f"score={score.get('lead_score')}, "
                f"priority={score.get('priority')}, "
                f"iterations={iteration + 1}"
            )
            return {**lead, **score}

        for tool_call in msg.tool_calls:
            logger.info(
                f"Scoring tool call [{company_name}]: "
                f"{tool_call.function.name}({tool_call.function.arguments})"
            )
            result = _dispatch_tool(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

    logger.warning(f"Max iterations reached for {company_name}, using fallback score")
    return _fallback_score(lead)


def score_leads(context, enriched_leads):

    start_time = time.time()
    logger.info("Starting lead scoring agent")

    scored = [_score_single_lead(context, lead) for lead in enriched_leads]

    scored = sorted(scored, key=lambda x: x["lead_score"], reverse=True)

    execution_time = round(time.time() - start_time, 2)
    logger.info(f"Lead scoring completed in {execution_time}s")

    return scored
