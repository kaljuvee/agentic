#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API credentials.
"""
import os
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

def test_openai_credentials():
    """Test OpenAI API credentials by making a simple API call."""
    # Load environment variables
    load_dotenv()
    
    # Get API key and model from environment
    api_key = os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    
    if not api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables.")
        return False
    
    print(f"Testing OpenAI API with model: {model_name}")
    
    try:
        # Initialize the model
        model = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            max_tokens=256,
            openai_api_key=api_key
        )
        
        # Create a simple message
        message = HumanMessage(content="Hello, can you give me a short joke?")
        
        # Time the API call
        start_time = time.time()
        response = model.invoke([message])
        end_time = time.time()
        
        # Print the response
        print("\nAPI Response:")
        print("-" * 50)
        print(response.content)
        print("-" * 50)
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
        print("\nAPI credentials are working correctly!")
        return True
        
    except Exception as e:
        print(f"\nERROR: Failed to connect to OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== OpenAI API Credentials Test ===")
    success = test_openai_credentials()
    
    if success:
        print("\nTest PASSED: Your OpenAI API credentials are valid.")
    else:
        print("\nTest FAILED: Please check your OpenAI API credentials.")
        print("Make sure your .env file contains a valid OPENAI_API_KEY.") 