from examples.alpaca_trader.trading_agent import get_response
from dotenv import load_dotenv

# Test cases for different trading operations
TEST_QUERIES = [
    {
        "query": "Show me my account information",
        "thread_id": "test_paper_account_info",
    },
    {
        "query": "Place a market order to buy 1 share of MSFT",
        "thread_id": "test_paper_market_order",
    },
    {
        "query": "Show me my current positions",
        "thread_id": "test_paper_positions",
    }
]

def test_trading_agent():
    """
    Test the Alpaca trading agent with paper trading operations
    """
    # Load environment variables
    load_dotenv()
    
    print("\nTesting Alpaca Paper Trading Agent")
    print("=" * 50)
    
    for test_case in TEST_QUERIES:
        print(f"\nTesting query: {test_case['query']}")
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
            print("\nConversation:")
            for message in response["messages"]:
                print(f"\n{message.type.upper()}: {message.content}")
            
            print("\n✅ Test case completed successfully")
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    # Run the tests
    test_trading_agent() 