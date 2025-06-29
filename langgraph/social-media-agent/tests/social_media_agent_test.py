import requests
import json
import sys
import uuid
import time
import os
import asyncio
from graph.social_media_agent import stream_response, get_response

def test_direct_query(query):
    """
    Test the social media agent directly without going through the FastAPI server.
    
    Args:
        query (str): The social media query to send to the agent
    """
    print(f"\nTEST QUERY (DIRECT): {query}")
    
    # Create a unique user ID for this session
    user_id = str(uuid.uuid4())
    
    try:
        print("Response:")
        print("-" * 50)
        
        # Run the async function to get the streaming response
        async def run_test():
            async for chunk in stream_response(query, user_id):
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

def test_sync_query(query):
    """
    Test the social media agent directly using the synchronous get_response function.
    
    Args:
        query (str): The social media query to send to the agent
    """
    print(f"\nTEST QUERY (SYNC): {query}")
    
    # Create a unique user ID for this session
    user_id = str(uuid.uuid4())
    
    try:
        print("Response:")
        print("-" * 50)
        
        # Get the response
        final_state = get_response(query, user_id)
        
        # Print the conversation
        for message in final_state["messages"]:
            if hasattr(message, 'content') and message.content:
                print(message.content)
        
        print("-" * 50)
        print("Test completed.")
        
        return "Response received"
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def run_social_media_tests():
    """
    Run a series of predefined test queries for the social media agent.
    """
    # Test cases for Social Media Agent
    TEST_QUERIES = [
        "Post 'Hello World!' to LinkedIn",
        "Post 'Excited to share our latest project!' to LinkedIn"
    ]
    
    print("Starting Social Media Agent Tests")
    print("=" * 70)
    
    results = []
    for i, query in enumerate(TEST_QUERIES):
        print(f"\nTest {i+1}/{len(TEST_QUERIES)}")
        
        # Try both methods
        print("\nTesting with streaming:")
        result_stream = test_direct_query(query)
        
        print("\nTesting with synchronous:")
        result_sync = test_sync_query(query)
        
        results.append((result_stream, result_sync))
        
        # Add a small delay between tests
        if i < len(TEST_QUERIES) - 1:
            time.sleep(1)
    
    print("\nAll tests completed!")
    print("=" * 70)
    
    return results

if __name__ == "__main__":
    # Run the social media tests automatically
    run_social_media_tests() 