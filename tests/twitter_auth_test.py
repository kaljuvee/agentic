import tweepy
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def test_simple_post():
    """
    Simple test to post a Hello World message using Twitter API v2
    """
    print("\nTesting simple tweet post...")
    try:
        # Initialize client with v2 authentication
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_KEY_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Hello World! 🌍 Testing Twitter API v2 integration. Timestamp: {timestamp}"
        response = client.create_tweet(text=message)
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        print(f"✅ Posted tweet: {tweet_url}")
        
    except Exception as e:
        print(f"❌ Error posting tweet: {str(e)}")
        raise

def test_twitter_auth():
    """
    Test Twitter API v2 authentication and validate read/write privileges
    """
    print("\nTesting Twitter API Authentication...")
    print("=" * 50)
    
    try:
        # Initialize client with v2 authentication
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_KEY_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Test 1: Verify credentials and get user info
        print("\n1. Testing user authentication...")
        me = client.get_me(user_fields=['username', 'id'])
        if not me.data:
            raise tweepy.TweepyException("Could not retrieve user data")
        print(f"✅ Authenticated as: @{me.data.username}")
        print(f"Account ID: {me.data.id}")
        
        # Test 2: Test read privileges
        print("\n2. Testing read privileges...")
        tweets = client.get_users_tweets(me.data.id, max_results=5)
        if tweets.data:
            print(f"✅ Successfully retrieved {len(tweets.data)} tweets")
        else:
            print("✅ Read access confirmed (no tweets found)")
            
        # Test 3: Test write privileges with a test tweet
        print("\n3. Testing write privileges...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_tweet = f"API v2 test tweet - {os.urandom(4).hex()} - {timestamp}"
        response = client.create_tweet(text=test_tweet)
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        print(f"✅ Successfully posted test tweet: {tweet_url}")
        
        # Test 4: Post Hello World tweet
        print("\n4. Posting Hello World tweet...")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hello_message = f"Hello World! 🌍 Testing Twitter API v2 integration. Timestamp: {timestamp}"
        hello_response = client.create_tweet(text=hello_message)
        hello_tweet_id = hello_response.data['id']
        hello_tweet_url = f"https://twitter.com/user/status/{hello_tweet_id}"
        print(f"✅ Posted Hello World tweet: {hello_tweet_url}")
        
        print("\n✅ All authentication tests passed successfully!")
        print("=" * 50)
        print("Privileges summary:")
        print("- Read access: ✅")
        print("- Write access: ✅")
        print(f"\nPosted tweets (please verify and delete manually):")
        print(f"1. Test tweet: {tweet_url}")
        print(f"2. Hello World tweet: {hello_tweet_url}")
        
    except tweepy.TweepyException as e:
        error_message = str(e)
        print(f"\n❌ Twitter API Error: {error_message}")
        
        # Provide more specific error feedback
        if "401" in error_message:
            print("\nAuthentication Error Details:")
            print("- Check if your API keys and tokens are correct")
            print("- Verify that your tokens haven't expired")
            print("- Ensure your app has the required permissions")
            print("- Confirm TWITTER_API_KEY_SECRET (not TWITTER_API_SECRET) is used")
        elif "403" in error_message:
            print("\nAuthorization Error Details:")
            print("- Your credentials are valid but you don't have permission for this action")
            print("- Check your app's permissions in the Twitter Developer Portal")
        
        raise
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the simple post test
    test_simple_post()
    
    # Run the full authentication test
    test_twitter_auth() 