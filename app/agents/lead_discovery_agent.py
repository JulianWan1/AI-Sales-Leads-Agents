import json
import time

from app.services.openai_service import client
from app.services.logger import logger
from app.tools.tavily_search_tool import tavily_search


MAX_TOOL_ITERATIONS = 8

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for potential sales leads. "
                "Call multiple times with different queries to cover different angles "
                "(e.g. by geography, company type, industry segment, or use case)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query to find relevant companies",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

SYSTEM_PROMPT = """You are a sales lead discovery AI.

Your task is to find REAL potential sales leads using web searches, then return them as JSON.

You have one tool:
- search_web: search the web for companies that match the business context

Discovery process:
1. Run multiple searches using different angles — vary by geography, company type, industry segment, or use case
2. Collect real company names from the search results
3. Once you have enough leads (aim for 5), return them as JSON

Rules:
- Company names MUST come from search results — do NOT invent companies
- Prefer companies strongly aligned with the ideal customer profile and product fit
- Return only the company name — qualification happens in a later stage

Output format (return ONLY a valid JSON array, no markdown):
[
  {
    "company": "Company Name"
  }
]"""


def _build_user_prompt(context):
    return f"""Find potential sales leads for this business.

Business Context:
- Industry: {context.industry}
- Product: {context.product}
- Ideal Customer: {context.ideal_customer}

Run multiple searches from different angles to find real companies that match this profile, then return the lead list as JSON."""


def _dispatch_tool(tool_call):
    args = json.loads(tool_call.function.arguments)

    if tool_call.function.name == "search_web":
        query = args["query"]
        logger.info(f"Discovery search: {query}")
        try:
            return tavily_search(query)
        except Exception as e:
            logger.warning(f"Search failed for query '{query}': {e}")
            return {"error": str(e)}

    return {"error": f"Unknown tool: {tool_call.function.name}"}


def generate_leads(context):

    start_time = time.time()
    logger.info("Starting lead discovery agent")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_prompt(context)},
    ]

    for iteration in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        msg = response.choices[0].message
        messages.append(msg)

        if response.choices[0].finish_reason == "stop":
            content = msg.content.strip().replace("```json", "").replace("```", "")
            leads = json.loads(content)
            execution_time = round(time.time() - start_time, 2)
            logger.info(
                f"Lead discovery completed in {execution_time}s — "
                f"{len(leads)} leads found across {iteration + 1} iterations"
            )
            return leads

        for tool_call in msg.tool_calls:
            result = _dispatch_tool(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

    logger.warning("Max iterations reached in lead discovery, returning empty list")
    return []
