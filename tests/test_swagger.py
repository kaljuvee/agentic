import requests
import json

def test_swagger_endpoints():
    """Test that Swagger documentation is accessible and valid"""
    #base_url = "http://localhost:5000"
    base_url = "https://agentic-dcjz.onrender.com"
    
    # Test Swagger endpoint
    swagger_response = requests.get(f"{base_url}/swagger")
    assert swagger_response.status_code == 200
    
    # Validate it's proper JSON
    swagger_json = swagger_response.json()
    assert swagger_json["openapi"] == "3.0.0"
    assert "/chat" in swagger_json["paths"]
    
    # Test the chat endpoint using the example from Swagger
    chat_response = requests.post(
        f"{base_url}/chat",
        json={
            "agent": "anchorman",
            "query": "What are the top business headlines today?"
        }
    )
    assert chat_response.status_code == 200
    assert "response" in chat_response.json()

if __name__ == "__main__":
    test_swagger_endpoints()
    print("✅ Swagger endpoints are working correctly") 