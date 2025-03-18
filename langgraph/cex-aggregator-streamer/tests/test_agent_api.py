import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API endpoint
#API_URL = "https://agentic-dcjz.onrender.com/chat"
API_URL = "http://localhost:8000/chat"  # Make sure this matches your FastAPI server port

# Test cases for CEX Aggregator Agent
TEST_QUERIES = [
        "What exchanges are available?",
        "Show me my balance on Binance",
        "What is the price of BTC/USDT on Bybit?"
    ]

def test_chat_endpoint():
    """
    Test the chat API endpoint with cryptocurrency exchange queries
    """
    for query in TEST_QUERIES:
        print(f"\nTesting query: {query}")
        print("=" * 50)
        
        # Prepare the request payload - match the expected format in run.py
        payload = {
            "input": query,  # Changed from "query" to "input" to match ChatRequest model
            "history": [],
            "config": {
                "thread_id": "test-api-user",
                "streaming": False  # Use non-streaming for easier testing
            }
        }
        
        try:
            # Print request details for debugging
            print(f"\nMaking request to: {API_URL}")
            print(f"Payload: {payload}")
            
            # Make POST request to the API
            response = requests.post(API_URL, json=payload)
            
            # Print response details for debugging
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Content: {response.text}")
            
            # Check if request was successful
            assert response.status_code == 200, f"Request failed with status code: {response.status_code}"
            
            # Parse response JSON
            response_data = response.json()
            
            # Basic validation of response structure
            assert "response" in response_data, "Response missing 'response' field"
            
            # Print the response for inspection
            print("\nResponse:")
            print(f"Message: {response_data['response']}")
            
            print("\n✅ Test completed successfully")
            
        except Exception as e:
            print(f"❌ Error during test: {str(e)}")
            raise

if __name__ == "__main__":
    test_chat_endpoint()
