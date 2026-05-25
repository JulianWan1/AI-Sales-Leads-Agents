import os
import requests

from app.services.logger import logger


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def extract_website_content(url: str) -> dict:

    logger.info(f"Extracting website content: {url}")

    try:
        response = requests.post(
            "https://api.tavily.com/extract",
            json={"api_key": TAVILY_API_KEY, "urls": [url]},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])

        if results:
            content = results[0].get("raw_content", "")[:8000]
            return {"success": True, "content": content}

        return {"success": False, "error": "No content extracted"}

    except Exception as e:
        logger.warning(f"Website extraction failed for {url}: {e}")
        return {"success": False, "error": str(e)}
