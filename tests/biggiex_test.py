from examples.twitter.biggiex import get_response

# Test cases for Biggie-style news raps
TEST_QUERIES = [
    {
        "query": "rap on president",
        "thread_id": "test_president_rap",
        "description": "Presidential news in Biggie style"
    },
    {
        "query": "rap on stock market",
        "thread_id": "test_stock_rap",
        "description": "Stock market news in Biggie style"
    }
]

def test_biggie_news_rapper():
    """
    Test the BiggieLLM news rapper agent
    """
    print("\n🎤 BiggieX News Rap Test Session 🎤")
    print("=" * 50)
    
    for test_case in TEST_QUERIES:
        print(f"\n📰 Testing: {test_case['description']}")
        print("-" * 50)
        
        try:
            response = get_response(
                test_case["query"], 
                thread_id=test_case["thread_id"]
            )
            
            # Basic validation
            if not response or "messages" not in response:
                print("❌ Error: Invalid response format")
                continue
            
            # Print the conversation
            print("\nConversation Flow:")
            for message in response["messages"]:
                if message.type == "assistant":
                    # Add BiggieX: prefix to the rap content
                    content = message.content
                    if "post_tweet" in content.lower():
                        # Extract the tweet text and add prefix
                        tweet_start = content.find('"') + 1
                        tweet_end = content.rfind('"')
                        if tweet_start > 0 and tweet_end > 0:
                            tweet_text = content[tweet_start:tweet_end]
                            modified_content = content[:tweet_start] + "BiggieX: " + tweet_text + content[tweet_end:]
                            print(f"\n🎵 BiggieX: {modified_content}")
                        else:
                            print(f"\n🎵 BiggieX: {content}")
                    else:
                        print(f"\n🎵 BiggieX: {content}")
                else:
                    print(f"\n👤 User: {message.content}")
            
            print("\n✅ Test case completed successfully")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    # Run the test
    test_biggie_news_rapper() 