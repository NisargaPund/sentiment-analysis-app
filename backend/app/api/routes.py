from __future__ import annotations

from flask import Blueprint, current_app, request, session

from ..auth.utils import login_required
from ..db import execute, query_all
from ..activity import log_activity
from ..twitter.client import TwitterClient
from ..twitter.mock_client import MockTwitterClient
from ..news.client import NewsAPIClient

api_bp = Blueprint("api", __name__)

_model = None

# Trending topics/news list (can be extended to fetch from news API)
TRENDING_TOPICS = [
    {"id": 1, "title": "India Budget 2025", "category": "Politics"},
    {"id": 2, "title": "Artificial Intelligence", "category": "Technology"},
    {"id": 3, "title": "Climate Change", "category": "Environment"},
    {"id": 4, "title": "Global Economy", "category": "Business"},
    {"id": 5, "title": "Space Exploration", "category": "Science"},
    {"id": 6, "title": "Electric Vehicles", "category": "Technology"},
    {"id": 7, "title": "Healthcare Innovation", "category": "Health"},
    {"id": 8, "title": "Cryptocurrency", "category": "Finance"},
    {"id": 9, "title": "Renewable Energy", "category": "Environment"},
    {"id": 10, "title": "Education Technology", "category": "Education"},
    {"id": 11, "title": "Social Media", "category": "Technology"},
    {"id": 12, "title": "Sports News", "category": "Sports"},
]


def _get_model():
    global _model
    if _model is None:
        try:
            from ..ml.sentiment import TwitterRobertaSentiment
            print("Loading RoBERTa model (first time - this may take 30-60 seconds)...")
            _model = TwitterRobertaSentiment()
            print("Model loaded successfully!")
        except ImportError as e:
            raise RuntimeError(
                "ML dependencies (transformers, torch) not installed. "
                "Install with: pip install transformers torch"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to load ML model: {str(e)}. "
                "This might be due to network issues downloading the model or insufficient disk space."
            ) from e
    return _model


@api_bp.get("/trending")
@login_required
def get_trending():
    """Get list of trending topics/news"""
    return {"topics": TRENDING_TOPICS}


@api_bp.post("/fetch-news")
@login_required
def fetch_news():
    """Fetch news articles/tweets for a given topic"""
    try:
        data = request.get_json(silent=True) or {}
        keyword = (data.get("keyword") or "").strip()
        if not keyword:
            return {"error": "keyword is required"}, 400

        max_results = int(current_app.config["TWEET_MAX_RESULTS"])
        data_source = current_app.config.get("DATA_SOURCE", "newsapi")
        
        # Try NewsAPI first (free), then Twitter, then demo mode
        if data_source == "newsapi" or (data_source != "twitter" and data_source != "demo"):
            news_api_key = current_app.config.get("NEWS_API_KEY", "")
            if news_api_key and news_api_key != "your-news-api-key":
                try:
                    news_client = NewsAPIClient(news_api_key)
                    articles = news_client.search_articles(keyword, max_results=max_results)
                    
                    if articles:
                        news_items = [
                            {
                                "id": article["id"],
                                "text": article["text"],
                                "title": article.get("title", ""),
                                "source": article.get("source", ""),
                                "topic": keyword
                            }
                            for article in articles
                        ]
                        log_activity("fetch_news", user_id=int(session["user_id"]), payload={"keyword": keyword, "count": len(news_items), "source": "NewsAPI"})
                        return {
                            "topic": keyword,
                            "news_items": news_items,
                            "count": len(news_items),
                            "source": "NewsAPI"
                        }
                except Exception as e:
                    # If NewsAPI fails, fall back to other options
                    print(f"NewsAPI failed: {e}, trying fallback...")
        
        # Fallback to Twitter API (if available)
        if data_source == "twitter":
            demo_mode = current_app.config.get("DEMO_MODE", False)
            
            if demo_mode:
                client = MockTwitterClient()
                query = keyword
            else:
                bearer_token = current_app.config["TWITTER_BEARER_TOKEN"]
                
                if not bearer_token or bearer_token == "your-twitter-api-v2-bearer-token":
                    return {
                        "error": "No data source configured. Set NEWS_API_KEY in .env for free real-time news, or TWITTER_BEARER_TOKEN for Twitter (requires paid plan)."
                    }, 500

                client = TwitterClient(bearer_token)
                query = f'({keyword}) lang:en -is:retweet'
            
            try:
                texts = client.recent_search(query=query, max_results=max_results)
            except RuntimeError as e:
                error_msg = str(e)
                if "402" in error_msg or "Payment Required" in error_msg:
                    return {
                        "error": "Twitter API requires paid subscription. Set NEWS_API_KEY in .env for free real-time news from NewsAPI.",
                        "suggestion": "Get free API key at https://newsapi.org/register"
                    }, 402
                raise

            if not texts:
                log_activity("fetch_news", user_id=int(session["user_id"]), payload={"keyword": keyword, "count": 0, "source": "Twitter"})
                return {
                    "news_items": [],
                    "message": "No news/tweets found for this topic. Try a different keyword."
                }

            news_items = [
                {"id": i + 1, "text": text, "topic": keyword}
                for i, text in enumerate(texts)
            ]
            log_activity("fetch_news", user_id=int(session["user_id"]), payload={"keyword": keyword, "count": len(news_items), "source": "Twitter"})
            return {
                "topic": keyword,
                "news_items": news_items,
                "count": len(news_items),
                "source": "Twitter"
            }
        
        # Final fallback: Demo mode
        client = MockTwitterClient()
        texts = client.recent_search(keyword, max_results=max_results)
        news_items = [
            {"id": i + 1, "text": text, "topic": keyword}
            for i, text in enumerate(texts)
        ]
        log_activity("fetch_news", user_id=int(session["user_id"]), payload={"keyword": keyword, "count": len(news_items), "source": "Demo"})
        return {
            "topic": keyword,
            "news_items": news_items,
            "count": len(news_items),
            "source": "Demo"
        }

    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return {"error": f"Failed to fetch news: {error_msg}"}, 500


@api_bp.post("/analyze")
@login_required
def analyze():
    """Analyze sentiment of a specific news item/text with explanation"""
    try:
        data = request.get_json(silent=True) or {}
        news_text = (data.get("news_text") or "").strip()
        topic = (data.get("topic") or "").strip()
        
        if not news_text:
            return {"error": "news_text is required"}, 400

        # Analyze single news item with explanation
        model = _get_model()
        analysis = model.analyze_with_explanation(news_text)

        # Store history (optional but implemented)
        user_id = int(session["user_id"])
        execute(
            """
            INSERT INTO searches (user_id, keyword, tweet_count, positive, neutral, negative)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, topic or "Custom", 1, analysis["probabilities"]["positive"], 
             analysis["probabilities"]["neutral"], analysis["probabilities"]["negative"]),
        )
        log_activity("analyze", user_id=user_id, payload={
            "topic": topic or "Custom",
            "sentiment": analysis["sentiment"],
            "confidence": analysis["confidence"],
            "positive": analysis["probabilities"]["positive"],
            "neutral": analysis["probabilities"]["neutral"],
            "negative": analysis["probabilities"]["negative"],
        })

        return {
            "news_text": news_text[:100] + "..." if len(news_text) > 100 else news_text,
            "full_text": news_text,
            "topic": topic,
            "sentiment": analysis["probabilities"],
            "classification": analysis["sentiment"],
            "confidence": analysis["confidence"],
            "explanation": analysis["explanation"],
            "key_words": analysis["key_words"]
        }
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return {"error": f"Analysis failed: {error_msg}"}, 500


@api_bp.get("/history")
@login_required
def get_history():
    """Get search history for the logged-in user"""
    try:
        from ..db import query_all
        
        user_id = int(session["user_id"])
        
        # Get all searches for this user, ordered by most recent first
        searches = query_all(
            """
            SELECT id, keyword, tweet_count, positive, neutral, negative, created_at
            FROM searches
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        
        # Calculate statistics
        total_searches = len(searches)
        total_tweets = sum(s["tweet_count"] for s in searches)
        
        # Calculate average sentiment
        if total_searches > 0:
            avg_positive = sum(s["positive"] for s in searches) / total_searches
            avg_neutral = sum(s["neutral"] for s in searches) / total_searches
            avg_negative = sum(s["negative"] for s in searches) / total_searches
        else:
            avg_positive = avg_neutral = avg_negative = 0.0
        
        return {
            "searches": searches,
            "statistics": {
                "total_searches": total_searches,
                "total_tweets_analyzed": total_tweets,
                "average_sentiment": {
                    "positive": round(avg_positive, 2),
                    "neutral": round(avg_neutral, 2),
                    "negative": round(avg_negative, 2)
                }
            }
        }
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback.print_exc()
        return {"error": f"Failed to fetch history: {error_msg}"}, 500

