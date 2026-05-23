import os
import requests

from app.services.logger import logger


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def tavily_search(query):

    logger.info(f"Tavily search: {query}")

    url = "https://api.tavily.com/search"

    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 5,
    }

    response = requests.post(
        url,
        json=payload,
        timeout=15,
    )

    response.raise_for_status()

    return response.json()