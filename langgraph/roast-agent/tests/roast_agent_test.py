import sys
import time
import os
from graph.roast_agent import get_roast_questions

def test_roast_agent(name):
    """
    Test the roast agent with a given name.
    
    Args:
        name (str): The name of the person to roast
    """
    print(f"\n=== Testing roast agent with: {name} ===")
    
    try:
        # Get the response
        start_time = time.time()
        roast_questions = get_roast_questions(name)
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
    """Run a series of tests for the roast agent."""
    # List of famous people to test
    test_names = [
        "Elon Musk",
        "Taylor Swift"
    ]
    
    # Run tests
    for name in test_names:
        test_roast_agent(name)
        
        # Add a small delay between tests
        if name != test_names[-1]:
            print("\nWaiting before next test...")
            time.sleep(2)

if __name__ == "__main__":
    run_roast_tests() 