# How to Check Your Database

## Method 1: Python Script (Easiest) ✅

Run this command from the `backend` folder:

```powershell
cd backend
.\.venv312\Scripts\Activate.ps1
python view_db.py
```

This will show:
- All users (ID, username, created date)
- All searches (user, keyword, sentiment results)
- Summary statistics

---

## Method 2: SQLite Command Line

If you have SQLite installed, you can use:

```powershell
cd backend
sqlite3 app.db
```

Then run SQL commands:
```sql
-- View all users
SELECT * FROM users;

-- View all searches
SELECT * FROM searches;

-- View searches with usernames
SELECT s.id, u.username, s.keyword, s.tweet_count, s.positive, s.neutral, s.negative
FROM searches s
JOIN users u ON s.user_id = u.id;

-- Exit
.quit
```

---

## Method 3: GUI Tool (Recommended for Visual Viewing)

### Option A: DB Browser for SQLite (Free)
1. Download: https://sqlitebrowser.org/
2. Install and open
3. Click "Open Database"
4. Navigate to: `backend/app.db`
5. Browse tables visually!

### Option B: VS Code Extension
1. Install "SQLite Viewer" extension in VS Code
2. Right-click `backend/app.db`
3. Select "Open Database"
4. Browse tables in VS Code!

---

## Quick SQL Queries

If you want to run custom queries, use the Python script or SQLite CLI:

```sql
-- Count users
SELECT COUNT(*) FROM users;

-- Find user by username
SELECT * FROM users WHERE username = 'Nisarga';

-- View recent searches
SELECT * FROM searches ORDER BY created_at DESC LIMIT 10;

-- Average sentiment by keyword
SELECT keyword, 
       AVG(positive) as avg_positive,
       AVG(neutral) as avg_neutral,
       AVG(negative) as avg_negative
FROM searches
GROUP BY keyword;
```

---

## Current Database Status

From the last check:
- **5 users** registered
- **4 searches** performed
- Database file: `backend/app.db`

---

## Need to Reset Database?

If you want to start fresh (⚠️ deletes all data):

```powershell
cd backend
Remove-Item app.db
# Restart backend - it will create a new empty database
```
