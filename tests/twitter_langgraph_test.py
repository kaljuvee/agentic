from examples.anchorman.langgraph.anchorman_agent import get_response
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Required API keys
REQUIRED_KEYS = [
    "NEWS_API_KEY", 
    "ANTHROPIC_API_KEY",
    "TWITTER_API_KEY",
    "TWITTER_API_SECRET",
    "TWITTER_ACCESS_TOKEN",
    "TWITTER_ACCESS_TOKEN_SECRET"
]

# Test cases with Twitter posting
TEST_QUERIES = [
    {
        "query": "summarize today's top tech news and post it to Twitter",
        "thread_id": "test_tech_twitter",
        "post_to_twitter": True
    },
    {
        "query": "what are the latest business headlines? Share a summary on Twitter",
        "thread_id": "test_business_twitter",
        "post_to_twitter": True
    },
    {
        "query": "just show me the sports news without posting to Twitter",
        "thread_id": "test_sports_no_twitter",
        "post_to_twitter": False
    }
]

def test_news_twitter_agent():
    """
    Test the news agent with Twitter integration
    """
    # Check for required API keys
    missing_keys = []
    for key in REQUIRED_KEYS:
        if not os.getenv(key):
            missing_keys.append(key)
    
    if missing_keys:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
    
    for test_case in TEST_QUERIES:
        query = test_case["query"]
        thread_id = test_case["thread_id"]
        post_to_twitter = test_case["post_to_twitter"]
        
        print(f"\n\nTesting query: {query}")
        print(f"Twitter posting: {'enabled' if post_to_twitter else 'disabled'}")
        print("=" * 50)
        
        try:
            response = get_response(
                query, 
                thread_id=thread_id,
                post_to_twitter=post_to_twitter
            )
            
            # Basic validation
            if not response or "messages" not in response:
                print("❌ Error: Invalid response format")
                continue
            
            # Print the conversation
            print("\nConversation:")
            for message in response["messages"]:
                print(f"\n{message.type.upper()}: {message.content}")
            
            # Validate Twitter posting
            if post_to_twitter:
                last_message = response["messages"][-1].content
                if "Successfully posted to Twitter" in last_message:
                    print("\n✅ Twitter posting successful")
                    # Extract and print Tweet ID if available
                    if "Tweet ID:" in last_message:
                        tweet_id = last_message.split("Tweet ID:")[-1].strip()
                        print(f"Tweet ID: {tweet_id}")
                else:
                    print("\n⚠️ Warning: Twitter post not confirmed in response")
            
            # Check for Ron Burgundy's signature phrases
            last_message = response["messages"][-1].content
            if not ("I'm Ron Burgundy" in last_message or "Stay classy" in last_message):
                print("\n⚠️ Warning: Missing Ron Burgundy's signature phrases")
            
            print("\n✅ Test case completed successfully")
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")

def test_twitter_credentials():
    """
    Test Twitter API credentials without posting
    """
    import tweepy
    
    print("\nTesting Twitter credentials...")
    try:
        auth = tweepy.OAuthHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET")
        )
        auth.set_access_token(
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Get authenticated user's information
        me = client.get_me()
        print(f"✅ Successfully authenticated as: @{me.data.username}")
        
    except Exception as e:
        print(f"❌ Twitter authentication failed: {str(e)}")
        raise

if __name__ == "__main__":
    # First test Twitter credentials
    test_twitter_credentials()
    
    # Then run the main tests
    test_news_twitter_agent() 