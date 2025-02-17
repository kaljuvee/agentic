from examples.twitter.langgraph.twitter_agent import get_response

# Test cases for different news categories
TEST_QUERIES = [
    {
        "query": "find news about artificial intelligence and post a summary",
        "thread_id": "test_ai_news",
        "query_term": "artificial intelligence"
    }
]

def test_news_twitter_agent():
    """
    Test the news agent with Twitter integration
    """
    # Test one query at a time to avoid rate limits
    test_case = TEST_QUERIES[0]  # Use the tech category test
    
    print(f"\nTesting query: {test_case['query']}")
    print("=" * 50)
    
    try:
        response = get_response(
            test_case["query"], 
            thread_id=test_case["thread_id"]
        )
        
        # Basic validation
        if not response or "messages" not in response:
            print("❌ Error: Invalid response format")
            return
        
        # Print the conversation
        print("\nConversation:")
        for message in response["messages"]:
            print(f"\n{message.type.upper()}: {message.content}")
        
        print("\n✅ Test case completed successfully")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    # Run the test
    test_news_twitter_agent() 