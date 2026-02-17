"""Test script to debug the analyze endpoint"""
import sys
from app import create_app

app = create_app()

with app.app_context():
    from app.api.routes import _get_model
    from app.twitter.client import TwitterClient
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    print("=" * 50)
    print("Testing Analyze Endpoint Components")
    print("=" * 50)
    
    # Test 1: Twitter Client
    print("\n1. Testing Twitter Client...")
    try:
        token = os.getenv("TWITTER_BEARER_TOKEN")
        if not token:
            print("   [ERROR] TWITTER_BEARER_TOKEN not set")
        else:
            print(f"   [OK] Token found (length: {len(token)})")
            client = TwitterClient(token)
            print("   [OK] TwitterClient created")
    except Exception as e:
        print(f"   [ERROR] Twitter Client error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: ML Model Loading
    print("\n2. Testing ML Model Loading...")
    try:
        print("   Loading model (this may take 30-60 seconds on first run)...")
        model = _get_model()
        print("   [OK] Model loaded successfully!")
    except Exception as e:
        print(f"   [ERROR] Model loading error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 3: Twitter API Call
    print("\n3. Testing Twitter API call...")
    try:
        query = "(India Budget) lang:en -is:retweet"
        texts = client.recent_search(query=query, max_results=10)
        print(f"   [OK] Got {len(texts)} tweets")
        if texts:
            print(f"   Sample tweet: {texts[0][:50]}...")
    except Exception as e:
        print(f"   [ERROR] Twitter API error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test 4: Sentiment Analysis
    if texts:
        print("\n4. Testing Sentiment Analysis...")
        try:
            agg = model.aggregate(texts)
            perc = agg.as_percentages()
            print(f"   [OK] Analysis complete!")
            print(f"   Results: {perc}")
        except Exception as e:
            print(f"   [ERROR] Sentiment analysis error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    print("\n" + "=" * 50)
    print("[OK] All tests passed!")
    print("=" * 50)
