import sys
import time
import os
from graph.roast_agent import get_roast_questions

def test_roast_agent(name, language="en"):
    """
    Test the roast agent with a given name and language.
    
    Args:
        name (str): The name of the person to roast
        language (str): Language code ("en" or "et")
    """
    print(f"\n=== Testing roast agent with: {name} (Language: {language}) ===")
    
    try:
        # Get the response
        start_time = time.time()
        roast_questions = get_roast_questions(name, language)
        end_time = time.time()
        
        # Print the response
        print("\nRoast Questions:")
        print("-" * 50)
        print(roast_questions)
        print("-" * 50)
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def run_roast_tests():
    """Run a series of tests for the roast agent in different languages."""
    # List of famous people to test
    test_names = [
        "Elon Musk",
        "Taylor Swift"
    ]
    
    # Test in English
    print("\n=== ENGLISH TESTS ===")
    for name in test_names:
        test_roast_agent(name, "en")
        if name != test_names[-1]:
            print("\nWaiting before next test...")
            time.sleep(2)
    
    # Test in Estonian
    print("\n=== ESTONIAN TESTS ===")
    for name in test_names:
        test_roast_agent(name, "et")
        if name != test_names[-1]:
            print("\nWaiting before next test...")
            time.sleep(2)

if __name__ == "__main__":
    run_roast_tests() 