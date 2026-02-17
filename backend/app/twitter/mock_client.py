"""Mock Twitter client for demo/testing when API access is not available"""
from typing import List


class MockTwitterClient:
    """Mock client that returns sample tweets for testing"""
    
    SAMPLE_TWEETS = [
        "Just read about the new budget proposal. This is amazing news for the economy!",
        "The budget announcement was disappointing. Not what we expected at all.",
        "Budget details are out. Seems pretty neutral to me, nothing special.",
        "Great budget! This will help small businesses thrive. Very positive development.",
        "The budget is terrible. This will hurt the middle class significantly.",
        "Budget announcement: Some good points, some concerns. Overall neutral impact.",
        "Love the new budget proposals! This is exactly what we needed. Very positive!",
        "Budget is a disaster. This will make things worse for everyone.",
        "The budget seems reasonable. Not too excited, not too disappointed.",
        "Fantastic budget! Great news for everyone. Very positive development!",
        "This budget is awful. Terrible decisions all around.",
        "Budget looks okay. Nothing groundbreaking, but acceptable.",
        "Amazing budget announcement! This will boost the economy significantly!",
        "The budget is concerning. Not sure about these changes.",
        "Budget seems fine. Standard updates, nothing special.",
    ]
    
    def __init__(self, bearer_token: str = "") -> None:
        """Initialize mock client (token not needed for demo)"""
        pass
    
    def recent_search(self, query: str, max_results: int = 50) -> List[str]:
        """
        Return mock tweets based on the keyword.
        For demo purposes, returns a mix of positive, negative, and neutral tweets.
        """
        keyword = query.lower()
        
        # Return a mix of sample tweets
        # In a real scenario, these would be filtered by keyword
        num_tweets = min(max_results, len(self.SAMPLE_TWEETS))
        return self.SAMPLE_TWEETS[:num_tweets]
