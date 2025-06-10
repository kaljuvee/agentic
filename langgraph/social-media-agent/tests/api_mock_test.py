import pytest
import asyncio
import uuid
import sys
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from run import app
from graph.social_media_agent import stream_response, get_response

# Create test client
client = TestClient(app)

def test_chat_endpoint():
    """Test the chat endpoint"""
    response = client.post(
        "/chat", 
        json={
            "input": "Show me my account information",
            "userId": "test-user",
            "messageHistory": []
        }
    )
    assert response.status_code == 200
    # Check that the content type contains text/event-stream
    assert "text/event-stream" in response.headers["content-type"]

def test_direct_query():
    """
    Test the alpaca agent directly using the get_response function.
    This is a simplified version that doesn't actually call the API.
    """
    # Create a mock for the graph.invoke method
    mock_invoke = MagicMock()
    
    # Create a mock response
    mock_response = {
        "messages": [
            MagicMock(content="Test response", type="ai")
        ]
    }
    mock_invoke.return_value = mock_response
    
    # Patch the graph object
    with patch("graph.alpaca_agent.graph") as mock_graph:
        mock_graph.invoke = mock_invoke
        
        # Import the function after patching
        from graph.social_media_agent import get_response
        
        # Test the get_response function
        result = get_response("Show me my account information", "test-user")
        
        # Verify the results
        assert result == mock_response
        mock_invoke.assert_called_once()

@pytest.mark.asyncio
async def test_stream_response():
    """
    Test the stream_response function.
    This is a simplified version that doesn't actually call the API.
    """
    # Create a mock for the astream method
    async def mock_astream(*args, **kwargs):
        # Create a mock message
        mock_message = MagicMock()
        mock_message.content = "Test response"
        
        # Yield a tuple of (stream_mode, chunk)
        yield "messages", (mock_message, {"langgraph_node": "agent"})
    
    # Patch the graph object
    with patch("graph.alpaca_agent.graph") as mock_graph:
        # Set up the mock
        mock_graph.astream = mock_astream
        
        # Import the function after patching
        from graph.social_media_agent import stream_response
        
        # Test the stream_response function
        chunks = []
        async for chunk in stream_response("Test query", "test-user"):
            chunks.append(chunk)
        
        # Verify the results
        assert len(chunks) > 0
        assert chunks[0].startswith("data: ")
        assert "Test response" in chunks[0]

def test_invalid_api_request():
    """Test an invalid API request"""
    response = client.post("/chat", json={"invalid": "data"})
    assert response.status_code == 422  # Validation error

def run_tests():
    """Run all the tests"""
    # Run the tests that don't require asyncio
    pytest.main(["-xvs", "test.py::test_chat_endpoint"])
    pytest.main(["-xvs", "test.py::test_direct_query"])
    pytest.main(["-xvs", "test.py::test_invalid_api_request"])
    
    # Run the async test separately
    pytest.main(["-xvs", "test.py::test_stream_response"])

if __name__ == "__main__":
    run_tests()
