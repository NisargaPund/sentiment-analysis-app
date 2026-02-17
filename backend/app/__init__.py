from flask import Flask, request
from flask_cors import CORS

from .config import Config
from .db import init_db
from .auth.routes import auth_bp
from .api.routes import api_bp
from .admin.routes import admin_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config())

    # Allow localhost and 127.0.0.1 on common Vite dev ports (5173–5180) so that
    # the dev server can talk to Flask with cookies regardless of which port Vite picks.
    origins = {app.config["FRONTEND_ORIGIN"]}
    for port in range(5173, 5181):
        origins.add(f"http://localhost:{port}")
        origins.add(f"http://127.0.0.1:{port}")
    CORS(app, supports_credentials=True, origins=list(origins))

    # Configure session cookie for local development
    # Using Lax works when both frontend and backend use same hostname (localhost)
    app.config["SESSION_COOKIE_DOMAIN"] = None  # Don't restrict domain
    app.config["SESSION_COOKIE_PATH"] = "/"

    init_db(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.get("/api/health")
    def health():
        return {"ok": True}
    
    @app.post("/api/test-session")
    def test_session():
        """Test endpoint to check if sessions are working"""
        from flask import session
        session["test"] = "working"
        return {
            "session_test": session.get("test"),
            "session_keys": list(session.keys()),
            "cookies_received": bool(request.cookies)
        }

    return app


# For gunicorn: run from backend/ with: gunicorn -w 1 -b 0.0.0.0:$PORT app:app
app = create_app()

