import requests
import json
import sys
import uuid
import time
import os
import asyncio
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to import the leisure_agent module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph.leisure_agent import stream_response, get_response

def ensure_test_data_dir():
    """Ensure the test-data directory exists."""
    test_data_dir = Path("test-data")
    test_data_dir.mkdir(exist_ok=True)
    return test_data_dir

def test_direct_query(query):
    """
    Test the OpenFlights travel agent directly without going through the FastAPI server.
    
    Args:
        query (str): The travel query to send to the agent
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
    Test the OpenFlights travel agent directly using the synchronous get_response function.
    
    Args:
        query (str): The travel query to send to the agent
    """
    print(f"\nTEST QUERY (SYNC): {query}")
    
    # Create a unique user ID for this session
    user_id = str(uuid.uuid4())
    
    try:
        print("Response:")
        print("-" * 50)
        
        # Get the response
        final_state = get_response(query, user_id)
        
        # Extract the response content
        response_content = ""
        for message in final_state["messages"]:
            if hasattr(message, 'content') and message.content:
                print(message.content)
                response_content += message.content + "\n"
        
        print("-" * 50)
        print("Test completed.")
        
        return {
            "status": "success",
            "response": response_content.strip(),
            "thread_id": user_id,
            "message_count": len(final_state["messages"])
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "thread_id": user_id
        }

def test_airport_queries():
    """Test various airport-related queries."""
    return [
        "What airports are available in New York?",
        "Show me information about JFK airport",
        "What airports are in London?",
        "Give me details about LAX airport",
        "Find airports in Tokyo",
        "What airports serve Paris?",
        "Show me information about Heathrow airport",
        "What airports are in Sydney?",
        "Give me details about ORD airport",
        "Find airports in Berlin"
    ]

def test_airline_queries():
    """Test various airline-related queries."""
    return [
        "What airlines operate in the United States?",
        "Give me information about American Airlines",
        "Show me details about Delta Airlines",
        "What airlines are based in Germany?",
        "Give me information about British Airways",
        "What airlines operate in Japan?",
        "Show me details about United Airlines",
        "What airlines are based in France?",
        "Give me information about Lufthansa",
        "What airlines operate in Australia?"
    ]

def test_route_queries():
    """Test various route-related queries."""
    return [
        "Find routes from JFK to LAX",
        "Show me routes from London to Paris",
        "What routes are available from Tokyo to Seoul?",
        "Find routes from Sydney to Melbourne",
        "Show me routes from Berlin to Frankfurt",
        "What routes are available from New York to London?",
        "Find routes from Los Angeles to San Francisco",
        "Show me routes from Paris to Rome",
        "What routes are available from Chicago to Miami?",
        "Find routes from Toronto to Vancouver"
    ]

def test_restaurant_queries():
    """Test various restaurant-related queries."""
    return [
        "Find restaurants in New York City",
        "Show me Italian restaurants in London",
        "What are the best restaurants in Paris?",
        "Find cheap restaurants in Tokyo",
        "Show me restaurants with 4+ star ratings in San Francisco",
        "What are the top restaurants in Rome?",
        "Find Mexican restaurants in Los Angeles",
        "Show me fine dining restaurants in Chicago",
        "What are the best seafood restaurants in Seattle?",
        "Find vegetarian restaurants in Berlin"
    ]

def test_restaurant_detail_queries():
    """Test restaurant detail queries."""
    return [
        "Give me details about a popular restaurant in New York",
        "Show me information about a well-rated restaurant in London",
        "What are the details of a famous restaurant in Paris?",
        "Tell me about a highly-rated restaurant in Tokyo",
        "Show me details of a restaurant in San Francisco"
    ]

def test_mixed_queries():
    """Test mixed travel and dining-related queries."""
    return [
        "What's the busiest airport in the world?",
        "Which airlines have the most international routes?",
        "What are the major hub airports in Europe?",
        "Show me airlines that operate long-haul flights",
        "What airports have the most international connections?",
        "Which airlines are known for their safety record?",
        "What are the main airports serving major cities?",
        "Show me budget airlines in Europe",
        "What airports are important for cargo operations?",
        "Which airlines have the most domestic routes?",
        "Find restaurants near JFK airport",
        "What are the best dining options in major tourist cities?",
        "Show me restaurants with good ratings near major airports",
        "What cuisine types are popular in different cities?",
        "Find restaurants that are open late near airports"
    ]

def run_comprehensive_travel_tests():
    """
    Run comprehensive tests for the leisure agent (travel and dining) and save results to JSON files.
    """
    # Ensure test data directory exists
    test_data_dir = ensure_test_data_dir()
    
    # Comprehensive test cases
    test_categories = {
        "airport_queries": test_airport_queries(),
        "airline_queries": test_airline_queries(),
        "route_queries": test_route_queries(),
        "restaurant_queries": test_restaurant_queries(),
        "restaurant_detail_queries": test_restaurant_detail_queries(),
        "mixed_queries": test_mixed_queries()
    }
    
    print("Starting Comprehensive Leisure Agent Tests (Travel & Dining)")
    print("=" * 80)
    
    # Generate timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    all_results = {
        "test_run_timestamp": timestamp,
        "test_categories": {},
        "summary": {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "total_response_time": 0
        }
    }
    
    for category_name, queries in test_categories.items():
        print(f"\n{'='*20} {category_name.upper()} {'='*20}")
        
        category_results = {
            "category": category_name,
            "queries": queries,
            "results": [],
            "summary": {
                "total": len(queries),
                "successful": 0,
                "failed": 0,
                "avg_response_time": 0
            }
        }
        
        total_time = 0
        
        for i, query in enumerate(queries):
            print(f"\nTest {i+1}/{len(queries)}: {query}")
            
            start_time = time.time()
            result = test_sync_query(query)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            # Add timing information to result
            result["query"] = query
            result["response_time"] = response_time
            result["test_number"] = i + 1
            
            category_results["results"].append(result)
            
            # Update summary
            if result["status"] == "success":
                category_results["summary"]["successful"] += 1
                all_results["summary"]["successful_tests"] += 1
            else:
                category_results["summary"]["failed"] += 1
                all_results["summary"]["failed_tests"] += 1
            
            all_results["summary"]["total_tests"] += 1
            all_results["summary"]["total_response_time"] += response_time
            
            # Add delay between tests to avoid overwhelming the API
            if i < len(queries) - 1:
                time.sleep(2)
        
        # Calculate average response time for category
        if category_results["summary"]["total"] > 0:
            category_results["summary"]["avg_response_time"] = total_time / category_results["summary"]["total"]
        
        all_results["test_categories"][category_name] = category_results
        
        # Save individual category results
        category_filename = f"test_results_{category_name}_{timestamp}.json"
        category_filepath = test_data_dir / category_filename
        
        with open(category_filepath, 'w') as f:
            json.dump(category_results, f, indent=2)
        
        print(f"\nCategory results saved to: {category_filepath}")
    
    # Calculate overall summary
    if all_results["summary"]["total_tests"] > 0:
        all_results["summary"]["avg_response_time"] = (
            all_results["summary"]["total_response_time"] / all_results["summary"]["total_tests"]
        )
    
    # Save complete results
    complete_filename = f"test_results_complete_{timestamp}.json"
    complete_filepath = test_data_dir / complete_filename
    
    with open(complete_filepath, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print final summary
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {all_results['summary']['total_tests']}")
    print(f"Successful: {all_results['summary']['successful_tests']}")
    print(f"Failed: {all_results['summary']['failed_tests']}")
    print(f"Success Rate: {(all_results['summary']['successful_tests']/all_results['summary']['total_tests']*100):.1f}%")
    print(f"Average Response Time: {all_results['summary']['avg_response_time']:.2f} seconds")
    print(f"Complete results saved to: {complete_filepath}")
    
    return all_results

def run_quick_travel_tests():
    """
    Run a quick set of essential tests for the leisure agent (travel and dining).
    """
    # Essential test cases for Leisure Agent
    TEST_QUERIES = [
        "What airports are available in New York?",
        "Show me information about JFK airport",
        "Find routes from JFK to LAX",
        "What airlines operate in the United States?",
        "Give me information about American Airlines",
        "Find restaurants in New York City",
        "Show me Italian restaurants in London",
        "What are the best restaurants in Paris?"
    ]
    
    print("Starting Quick Leisure Agent Tests (Travel & Dining)")
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
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Run quick tests
        run_quick_travel_tests()
    else:
        # Run comprehensive tests by default
        run_comprehensive_travel_tests() 