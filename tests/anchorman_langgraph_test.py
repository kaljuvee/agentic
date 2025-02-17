from examples.anchorman.langgraph.anchorman_agent import get_response
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Required API keys
REQUIRED_KEYS = ["NEWS_API_KEY", "ANTHROPIC_API_KEY"]

# Test cases
TEST_QUERIES = [
    ("show me the financial headlines today", "test_financial"),
    ("what's happening in technology?", "test_tech"),
    ("give me the latest sports news", "test_sports")
]

def test_news_agent():
    """
    Test the news agent with various queries
    """
    # Check for required API keys
    for key in REQUIRED_KEYS:
        if not os.getenv(key):
            raise ValueError(f"Missing required environment variable: {key}")
    
    for query, thread_id in TEST_QUERIES:
        print(f"\n\nTesting query: {query}")
        print("=" * 50)
        
        try:
            response = get_response(query, thread_id=thread_id)
            
            # Basic validation
            if not response or "messages" not in response:
                print("❌ Error: Invalid response format")
                continue
                
            # Check for Ron Burgundy's signature phrases
            last_message = response["messages"][-1].content
            if not ("I'm Ron Burgundy" in last_message or "Stay classy" in last_message):
                print("⚠️ Warning: Missing Ron Burgundy's signature phrases")
            
            # Print the conversation
            print("\nConversation:")
            for message in response["messages"]:
                print(f"\n{message.type.upper()}: {message.content}")
            
            print("\n✅ Test completed successfully")
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_news_agent()
