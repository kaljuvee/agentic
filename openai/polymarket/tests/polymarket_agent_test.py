import json
from datetime import datetime
import os
from dotenv import load_dotenv
from agent.polymarket_agent import (
    _get_active_open_markets,
    _get_market_details,
    _get_market_summary,
    get_active_open_markets,
    get_market_details,
    get_market_summary,
    create_agent,
    Config
)
import asyncio
from agents import Runner

# Load environment variables
load_dotenv()

def ensure_test_data_dir():
    """Ensure the test-data directory exists."""
    os.makedirs("test-data", exist_ok=True)

def run_test_case(name: str, func, *args, **kwargs):
    """Run a test case and return the results."""
    print(f"\nRunning test case: {name}")
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
        print(f"✓ {name} completed successfully")
    except Exception as e:
        result = None
        success = False
        error = str(e)
        print(f"✗ {name} failed: {error}")
    
    return {
        "name": name,
        "success": success,
        "result": result,
        "error": error,
        "timestamp": datetime.now().isoformat()
    }

def main():
    """Run all test cases and save results."""
    ensure_test_data_dir()
    
    # Initialize test results
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    # Test case 1: Get active markets
    test_results["tests"].append(
        run_test_case("get_active_markets", _get_active_open_markets, limit=5)
    )
    
    # Test case 2: Get markets with keywords
    test_results["tests"].append(
        run_test_case("get_markets_with_keywords", _get_active_open_markets, 
                     keywords=["election", "bitcoin"])
    )
    
    # Test case 3: Get market summary
    test_results["tests"].append(
        run_test_case("get_market_summary", _get_market_summary)
    )
    
    # Test case 4: Get specific market details
    # First get a market ID from the active markets
    markets_result = _get_active_open_markets(limit=1)
    if "Market ID:" in markets_result:
        market_id = markets_result.split("Market ID:")[1].split(",")[0].strip()
        test_results["tests"].append(
            run_test_case("get_market_details", _get_market_details, market_id)
        )
    
    # Test case 5: Agent creation and basic interaction
    try:
        agent = create_agent()
        test_results["tests"].append({
            "name": "agent_creation",
            "success": True,
            "result": "Agent created successfully",
            "error": None,
            "timestamp": datetime.now().isoformat()
        })
        
        # Test case 6: Agent interaction with a simple query
        async def agent_query():
            return await Runner.run(agent, input="What are the most active markets right now?")
        response = asyncio.run(agent_query())
        test_results["tests"].append({
            "name": "agent_basic_query",
            "success": True,
            "result": str(response.final_output) if hasattr(response, 'final_output') else str(response),
            "error": None,
            "timestamp": datetime.now().isoformat()
        })

        # Test case 7: Agent capabilities query
        async def capabilities_query():
            return await Runner.run(agent, input="What can you help me with?")
        response = asyncio.run(capabilities_query())
        test_results["tests"].append({
            "name": "agent_capabilities_query",
            "success": True,
            "result": str(response.final_output) if hasattr(response, 'final_output') else str(response),
            "error": None,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        test_results["tests"].append({
            "name": "agent_tests",
            "success": False,
            "result": None,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    
    # Save results to JSON file
    filename = f"test-data/test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nTest results saved to: {filename}")
    
    # Print summary
    total_tests = len(test_results["tests"])
    successful_tests = sum(1 for test in test_results["tests"] if test["success"])
    print(f"\nTest Summary:")
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")

if __name__ == '__main__':
    main() 