# Backend (Flask + Twitter API v2 + RoBERTa Sentiment)

## Prerequisites (important)
- **Python 3.11 or 3.12 recommended on Windows**
  - `transformers` depends on `tokenizers`, and for very new Python versions pip may attempt a source build (needs Rust/Cargo + MSVC).

## Setup (PowerShell)

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy env.example .env
```

Edit `.env` and set:
- `SECRET_KEY`
- `TWITTER_BEARER_TOKEN`

Run:

```powershell
python -m flask --app app run --debug
```

## API
- `POST /api/auth/signup` `{username,password}`
- `POST /api/auth/login` `{username,password}`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `POST /api/analyze` `{keyword}` (requires session)

