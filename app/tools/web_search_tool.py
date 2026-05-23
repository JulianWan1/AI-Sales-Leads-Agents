from app.services.logger import logger
from app.tools.tavily_search_tool import tavily_search


def search_company(company_name: str, focus: str = "") -> dict:

    query = f"{company_name} {focus}".strip()

    logger.info(f"Searching company: {query}")

    try:
        result = tavily_search(query)
        results = result.get("results", [])
        snippets = [
            {
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content"),
            }
            for r in results
        ]
        return {"success": True, "results": snippets}

    except Exception as e:
        logger.warning(f"Company search failed for {company_name}: {e}")
        return {"success": False, "error": str(e)}
