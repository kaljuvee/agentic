import requests
import json
import sys
import uuid
import time
import os
import asyncio
from graph.x_posting_agent import stream_response, get_response

# Test cases for neutral news commentary
TEST_QUERIES = [
    {
        "query": "news on China",
        "thread_id": "test_china_news",
        "description": "China news in neutral style"
    },
    {
        "query": "news on stock market",
        "thread_id": "test_stock_news",
        "description": "Stock market news in neutral style"
    }
]

def test_direct_query(test_case):
    """
    Test the X-posting agent directly with streaming response.
    
    Args:
        test_case (dict): The test case containing query, thread_id, and description
    """
    query = test_case["query"]
    thread_id = test_case["thread_id"]
    description = test_case["description"]
    
    print(f"\nTEST QUERY (STREAMING): {query}")
    print(f"Description: {description}")
    print(f"Thread ID: {thread_id}")
    
    try:
        print("Response:")
        print("-" * 50)
        
        # Run the async function to get the streaming response
        async def run_test():
            async for chunk in stream_response(query, thread_id):
                if chunk.startswith('data: '):
                    content = chunk[6:].strip()
                    sys.stdout.write(content)
                    sys.stdout.flush()
            
            # Print a newline at the end
            sys.stdout.write("\n")
            sys.stdout.flush()
        
        # Run the async function
        asyncio.run(run_test())
        
        print("-" * 50)
        print("Test completed.")
        
        return "Response received"
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_sync_query(test_case):
    """
    Test the X-posting agent directly using the synchronous get_response function.
    
    Args:
        test_case (dict): The test case containing query, thread_id, and description
    """
    query = test_case["query"]
    thread_id = test_case["thread_id"]
    description = test_case["description"]
    
    print(f"\nTEST QUERY (SYNC): {query}")
    print(f"Description: {description}")
    print(f"Thread ID: {thread_id}")
    
    try:
        print("Response:")
        print("-" * 50)
        
        # Get the response
        response, tweet_url = get_response(query, thread_id)
        
        # Print the response
        print(response)
        
        # Display tweet URL if available
        if tweet_url:
            print(f"\n🔗 Tweet URL: {tweet_url}")
            print(f"✅ Successfully posted to Twitter!")
        else:
            print("\n⚠️ No tweet was posted")
        
        print("-" * 50)
        print("Test completed.")
        
        return "Response received"
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def run_news_tests():
    """
    Run a series of predefined test queries for the X-posting agent.
    """
    print("Starting X-Posting Agent Tests")
    print("=" * 70)
    
    results = []
    for i, test_case in enumerate(TEST_QUERIES):
        print(f"\nTest {i+1}/{len(TEST_QUERIES)}: {test_case['description']}")
        
        # Try both methods
        print("\nTesting with streaming:")
        result_stream = test_direct_query(test_case)
        
        print("\nTesting with synchronous:")
        result_sync = test_sync_query(test_case)
        
        results.append((result_stream, result_sync))
        
        # Add a small delay between tests
        if i < len(TEST_QUERIES) - 1:
            time.sleep(1)
    
    print("\nAll tests completed!")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    # Run the news tests automatically
    run_news_tests() 