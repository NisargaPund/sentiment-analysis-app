"""Simple script to view database contents"""
import sqlite3
from pathlib import Path

DB_PATH = "app.db"

if not Path(DB_PATH).exists():
    print(f"❌ Database file '{DB_PATH}' not found!")
    exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=" * 60)
print("DATABASE CONTENTS")
print("=" * 60)

# View Users
print("\n[USERS TABLE]")
print("-" * 60)
cur.execute("SELECT id, username, created_at FROM users ORDER BY id")
users = cur.fetchall()
if users:
    print(f"{'ID':<5} {'Username':<20} {'Created At'}")
    print("-" * 60)
    for user in users:
        print(f"{user['id']:<5} {user['username']:<20} {user['created_at']}")
    print(f"\nTotal users: {len(users)}")
else:
    print("No users found.")

# View Searches
print("\n\n[SEARCHES TABLE]")
print("-" * 60)
cur.execute("""
    SELECT s.id, u.username, s.keyword, s.tweet_count, 
           s.positive, s.neutral, s.negative, s.created_at
    FROM searches s
    JOIN users u ON s.user_id = u.id
    ORDER BY s.id DESC
    LIMIT 20
""")
searches = cur.fetchall()
if searches:
    print(f"{'ID':<5} {'User':<15} {'Keyword':<20} {'Count':<8} {'Positive':<10} {'Neutral':<10} {'Negative':<10} {'Date'}")
    print("-" * 100)
    for search in searches:
        print(f"{search['id']:<5} {search['username']:<15} {search['keyword'][:18]:<20} "
              f"{search['tweet_count']:<8} {search['positive']:<10.1f} {search['neutral']:<10.1f} "
              f"{search['negative']:<10.1f} {search['created_at']}")
    print(f"\nTotal searches: {len(searches)}")
else:
    print("No searches found.")

# Summary
print("\n\n[SUMMARY]")
print("-" * 60)
cur.execute("SELECT COUNT(*) as count FROM users")
user_count = cur.fetchone()['count']
cur.execute("SELECT COUNT(*) as count FROM searches")
search_count = cur.fetchone()['count']
print(f"Total Users: {user_count}")
print(f"Total Searches: {search_count}")

conn.close()
print("\n" + "=" * 60)
