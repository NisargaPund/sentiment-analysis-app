# Real-Time Sentiment Analysis of Twitter News Using NLP

College-level intermediate web app for **near real-time sentiment analysis** on Twitter (X) topics.

## Tech Stack (as requested)
- **Frontend**: React.js + Tailwind CSS + Chart.js
- **Backend**: Python + Flask
- **ML**: Hugging Face Transformers (`cardiffnlp/twitter-roberta-base-sentiment`)
- **External API**: Twitter API v2 (Recent Search)
- **Auth**: Flask session-based authentication
- **DB**: SQLite

## 📋 Complete Setup Guide

### Prerequisites Check

1. **Python 3.11 or 3.12** (required for transformers/torch compatibility)
   ```powershell
   py -3.12 --version
   # OR
   python --version
   ```
   ⚠️ **Important**: Python 3.14 may cause issues with `tokenizers` package.

2. **Node.js and npm** (for React frontend)
   ```powershell
   node --version
   npm --version
   ```
   Should be Node 16+ and npm 8+.

3. **Twitter Developer Account** (for API access)
   - Go to https://developer.twitter.com
   - Sign up/login with your Twitter/X account

---

## Step 1: Get Twitter API v2 Bearer Token

1. **Go to Twitter Developer Portal**:
   - Visit: https://developer.twitter.com/en/portal/dashboard
   - Sign in with your Twitter/X account

2. **Create a Project** (if you don't have one):
   - Click "Create Project"
   - Fill in project name, use case (e.g., "Student Project - Sentiment Analysis")
   - Select "Making a bot" or "Exploring the API"
   - Complete the form

3. **Create an App** (within your project):
   - Click "Create App"
   - Give it a name (e.g., "sentiment-analysis-app")
   - Note your App ID

4. **Generate Bearer Token**:
   - Go to your app's "Keys and tokens" tab
   - Under "Bearer Token", click "Generate"
   - **Copy the token immediately** (you won't see it again!
   - Save it securely (you'll need it in Step 3)

5. **Set API Access Level** (if needed):
   - Make sure your app has access to "Read" tweets
   - Free tier allows 10,000 tweets/month

---

## Step 2: Backend Setup (Flask + Python)

### 2.1 Create Virtual Environment

Open PowerShell in the project root:

```powershell
cd "D:\cursor\nirjaala project\backend"

# Create venv with Python 3.11 or 3.12
py -3.12 -m venv .venv
# OR if python points to 3.11/3.12:
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```

You should see `(.venv)` in your prompt.

### 2.2 Install Backend Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Expected time**: 5-10 minutes (downloads Flask, transformers, torch, etc.)

**If you get errors**:
- **"No module named 'flask'"**: Make sure venv is activated (see `.venv` in prompt)
- **"torch/tokenizers build error"**: Use Python 3.11 or 3.12, not 3.14
- **"Rust/Cargo not found"**: This means tokenizers needs to compile. Use Python 3.11/3.12 to get prebuilt wheels.

### 2.3 Configure Environment Variables

```powershell
# Copy the example file
copy env.example .env

# Edit .env file (use Notepad, VS Code, or any editor)
notepad .env
```

**Edit `.env` file** with your values:

```env
# Generate a random secret key (for session security)
# You can use: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-long-random-secret-key-here-change-this

# Paste your Twitter Bearer Token from Step 1
TWITTER_BEARER_TOKEN=your-actual-bearer-token-from-twitter

# Keep these defaults for local development
SESSION_COOKIE_SECURE=false
FRONTEND_ORIGIN=http://localhost:5173
SQLITE_PATH=app.db
TWEET_MAX_RESULTS=50
```

**Generate SECRET_KEY** (run this in PowerShell):
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```
Copy the output and paste it as `SECRET_KEY` in `.env`.

### 2.4 Run the Backend

```powershell
# Make sure venv is activated (you should see (.venv) in prompt)
python -m flask --app app run --debug --host localhost
```

**Expected output**:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://localhost:5000
```

✅ **Backend is running!** Keep this terminal open.

**Test it**: Open http://localhost:5000/api/health in your browser. You should see `{"ok": true}`.

---

## Step 3: Frontend Setup (React)

### 3.1 Install Frontend Dependencies

Open a **new PowerShell window** (keep backend running):

```powershell
cd "D:\cursor\nirjaala project\frontend"

# Install npm packages
npm install
```

**Expected time**: 1-2 minutes

### 3.2 Run the Frontend

```powershell
npm run dev
```

**Expected output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

✅ **Frontend is running!** Keep this terminal open too.

---

## Step 4: Test the Application

1. **Open your browser**: Go to http://localhost:5173

2. **Create an account**:
   - Click "Signup"
   - Enter a username and password (min 6 characters)
   - Click "Create account"

3. **You should see the Dashboard** with:
   - Keyword input field
   - "Fetch Tweets" button
   - Empty sentiment metrics

4. **Test sentiment analysis**:
   - Enter a keyword (e.g., "India Budget", "AI", "technology")
   - Click "Fetch Tweets"
   - Wait 10-30 seconds (first run downloads the ML model)
   - You should see:
     - Total tweets analyzed
     - Positive/Negative/Neutral percentages
     - A pie chart visualization

---

## Step 5: Troubleshooting

### Issue: "unauthorized" error when clicking "Fetch Tweets"

**Solution**:
1. Clear browser cookies for `localhost`:
   - Press `F12` → Application tab → Cookies → Delete all for `localhost:5173` and `localhost:5000`
2. Hard refresh: `Ctrl+Shift+R`
3. Log out and log in again
4. Try "Fetch Tweets" again

### Issue: "TWITTER_BEARER_TOKEN is not set"

**Solution**:
1. Make sure `.env` file exists in `backend/` folder
2. Check that `TWITTER_BEARER_TOKEN=your-token` is in `.env` (no quotes)
3. Restart the Flask backend after editing `.env`

### Issue: "ML dependencies not installed"

**Solution**:
1. Make sure you're using Python 3.11 or 3.12
2. Activate venv: `.\.venv\Scripts\Activate.ps1`
3. Install: `pip install transformers torch`
4. Restart backend

### Issue: Backend won't start

**Check**:
- Is port 5000 already in use? Close other Flask apps
- Is venv activated? (should see `(.venv)` in prompt)
- Are dependencies installed? Run `pip list | findstr flask`

### Issue: Frontend shows "Failed to fetch"

**Check**:
- Is backend running? Test http://localhost:5000/api/health
- Check browser console (F12) for CORS errors
- Make sure frontend uses `http://localhost:5000` (not `127.0.0.1`)

### Issue: No tweets returned

**Possible causes**:
- Twitter API rate limit exceeded (free tier: 10k tweets/month)
- Bearer token invalid or expired
- Keyword too specific (try broader terms)
- Check backend terminal for error messages

---

## Project Structure

```
nirjaala project/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory
│   │   ├── config.py             # Configuration
│   │   ├── db.py                 # SQLite database
│   │   ├── auth/
│   │   │   ├── routes.py         # Signup/login endpoints
│   │   │   └── utils.py          # Auth helpers
│   │   ├── api/
│   │   │   └── routes.py         # /api/analyze endpoint
│   │   ├── ml/
│   │   │   └── sentiment.py     # RoBERTa sentiment model
│   │   └── twitter/
│   │       └── client.py         # Twitter API v2 client
│   ├── app.py                    # Flask entry point
│   ├── requirements.txt          # Python dependencies
│   ├── env.example               # Environment template
│   └── .env                      # Your config (create this)
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── App.jsx           # Main app router
    │   │   ├── Login.jsx         # Login page
    │   │   ├── Signup.jsx        # Signup page
    │   │   └── Dashboard.jsx     # Sentiment dashboard
    │   ├── components/           # Reusable components
    │   ├── lib/
    │   │   └── api.js            # API client
    │   └── main.jsx              # React entry point
    ├── package.json              # Node dependencies
    └── vite.config.js           # Vite config
```

---

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create account
- `POST /api/auth/login` - Sign in
- `POST /api/auth/logout` - Sign out
- `GET /api/auth/me` - Get current user

### Analysis
- `POST /api/analyze` - Analyze tweets (requires login)
  - Body: `{"keyword": "your topic"}`
  - Returns: `{keyword, tweet_count, sentiment: {positive, neutral, negative}}`

---

## Development Notes

- **Database**: SQLite file (`app.db`) is created automatically on first run
- **Sessions**: Uses Flask sessions with HTTP-only cookies
- **CORS**: Configured for `localhost:5173` (frontend) → `localhost:5000` (backend)
- **ML Model**: Downloads automatically on first use (~500MB, one-time)

---

## Next Steps (Optional Enhancements)

- Add search history view (show past analyses)
- Add date range filtering for tweets
- Add more chart types (bar chart, time series)
- Add export functionality (CSV/JSON)
- Add user preferences (default max_results, etc.)

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Check backend terminal for error messages
3. Check browser console (F12) for frontend errors
4. Verify all environment variables are set correctly

Good luck with your project! 🚀