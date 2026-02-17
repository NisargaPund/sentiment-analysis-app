from __future__ import annotations

from typing import List

import requests


class TwitterClient:
    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: str) -> None:
        self.bearer_token = bearer_token

    def recent_search(self, query: str, max_results: int = 50) -> List[str]:
        if not self.bearer_token:
            raise RuntimeError("TWITTER_BEARER_TOKEN is not set")

        url = f"{self.BASE_URL}/tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "lang,created_at",
        }
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        
        # Handle specific error cases
        if resp.status_code == 402:
            raise RuntimeError(
                "Twitter API v2 Recent Search requires a paid subscription. "
                "The free tier no longer includes access to this endpoint. "
                "You need Twitter API Basic ($100/month) or higher. "
                "For a college project, consider using mock data or Twitter API v1.1 if available."
            )
        elif resp.status_code == 401:
            raise RuntimeError("Twitter API authentication failed. Check your Bearer Token.")
        elif resp.status_code == 429:
            raise RuntimeError("Twitter API rate limit exceeded. Please wait and try again later.")
        
        resp.raise_for_status()
        data = resp.json()
        tweets = data.get("data") or []
        # Return tweet texts only
        return [t.get("text", "") for t in tweets if t.get("text")]

