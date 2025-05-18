import requests
import json

# Sample curl commands for reference:
# curl -X POST "http://localhost:8000/chat" \
#      -H "Content-Type: application/json" \
#      -d '{"input": "What are the most active markets right now?"}'
#
# curl -X POST "http://localhost:8000/chat" \
#      -H "Content-Type: application/json" \
#      -d '{"input": "What can you help me with?"}'

def test_chat_endpoint():
    url = "http://localhost:8000/chat"
    
    # Test market query
    market_payload = {"input": "What are the most active markets right now?"}
    headers = {"Content-Type": "application/json"}
    
    print("\nTesting market query:")
    response = requests.post(url, data=json.dumps(market_payload), headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    
    # Test capabilities query
    capabilities_payload = {"input": "What can you help me with?"}
    
    print("\nTesting capabilities query:")
    response = requests.post(url, data=json.dumps(capabilities_payload), headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    test_chat_endpoint()
