"""NewsAPI client for fetching real-time news articles"""
from __future__ import annotations

from typing import List, Dict

import requests


class NewsAPIClient:
    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def search_articles(self, query: str, max_results: int = 20) -> List[Dict[str, str]]:
        """
        Search for news articles by keyword.
        Returns list of articles with title and description.
        """
        if not self.api_key:
            raise RuntimeError("NEWS_API_KEY is not set")

        url = f"{self.BASE_URL}/everything"
        params = {
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": min(max_results, 100),  # NewsAPI max is 100
            "apiKey": self.api_key,
        }
        
        headers = {"User-Agent": "Twitter-Sentiment-Analysis/1.0"}
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        
        if resp.status_code == 401:
            raise RuntimeError("NewsAPI authentication failed. Check your API key.")
        elif resp.status_code == 429:
            raise RuntimeError("NewsAPI rate limit exceeded. Free tier: 100 requests/day.")
        
        resp.raise_for_status()
        data = resp.json()
        
        articles = data.get("articles", [])
        # Return articles with title and description combined as text
        result = []
        for article in articles:
            title = article.get("title", "")
            description = article.get("description", "") or ""
            # Combine title and description for analysis
            text = f"{title}. {description}".strip()
            if text:
                result.append({
                    "id": len(result) + 1,
                    "text": text,
                    "title": title,
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", "")
                })
        
        return result[:max_results]
