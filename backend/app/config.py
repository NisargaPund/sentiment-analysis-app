import os
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv

# Backend root (parent of 'app' package) for resolving relative paths
_BACKEND_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Config:
    def __post_init__(self) -> None:
        # Load .env from backend folder so it works when run from project root
        load_dotenv(_BACKEND_ROOT / ".env")

        self.SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
        self.FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:5173")

        self.SESSION_COOKIE_HTTPONLY = True
        # For local dev: both frontend (localhost:5173) and backend (localhost:5000) are same-site,
        # so SameSite=Lax works. In production with HTTPS, use SameSite=None and Secure=True.
        # Check if we're in production (HTTPS frontend origin)
        is_production = self.FRONTEND_ORIGIN.startswith("https://")
        # For local development, use Lax which works for same-site requests
        # Note: Both frontend and backend should use localhost (not 127.0.0.1) for sessions to work
        self.SESSION_COOKIE_SAMESITE = "None" if is_production else "Lax"
        self.SESSION_COOKIE_SECURE = is_production
        # Set session lifetime for local dev (31 days default)
        from datetime import timedelta
        self.PERMANENT_SESSION_LIFETIME = timedelta(days=31)

        sqlite_path = os.getenv("SQLITE_PATH", "app.db")
        # Resolve relative path so db is always in backend folder (works from any cwd)
        self.SQLITE_PATH = sqlite_path if os.path.isabs(sqlite_path) else str(_BACKEND_ROOT / sqlite_path)

        self.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
        self.TWEET_MAX_RESULTS = int(os.getenv("TWEET_MAX_RESULTS", "50"))
        
        # NewsAPI for real-time news (free alternative to Twitter)
        self.NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
        
        # Demo mode: Use mock Twitter client instead of real API (for testing without paid API)
        self.DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        # Data source preference: "newsapi" (free), "twitter" (paid), or "demo" (mock)
        self.DATA_SOURCE = os.getenv("DATA_SOURCE", "newsapi").lower()
        
        # Admin credentials (set in .env for security)
        self.ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
        self.ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

