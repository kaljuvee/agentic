import os
import sys
import requests
import json
import time
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path to import the leisure_agent module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from graph.leisure_agent import search_restaurants, get_restaurant_details, TRIPADVISOR_API_KEY, TRIPADVISOR_BASE_URL

def ensure_test_data_dir():
    """Ensure the test-data directory exists."""
    test_data_dir = Path("test-data")
    test_data_dir.mkdir(exist_ok=True)
    return test_data_dir

def test_tripadvisor_api_connection():
    """Test basic TripAdvisor API connection."""
    print("Testing TripAdvisor API Connection...")
    
    if not TRIPADVISOR_API_KEY:
        print("❌ TRIPADVISOR_API_KEY not set in environment variables")
        return False
    
    try:
        # Test basic API connection with a simple search
        test_url = f"{TRIPADVISOR_BASE_URL}/location/search"
        params = {
            'key': TRIPADVISOR_API_KEY,
            'searchQuery': 'New York',
            'category': 'restaurants',
            'language': 'en'
        }
        
        response = requests.get(test_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if data.get('data'):
            print("✅ TripAdvisor API connection successful")
            return True
        else:
            print("❌ TripAdvisor API returned no data")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ TripAdvisor API connection failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

def test_search_restaurants_basic():
    """Test basic restaurant search functionality."""
    print("\nTesting Basic Restaurant Search...")
    
    test_cases = [
        {
            "location": "New York City",
            "description": "Basic search in NYC"
        },
        {
            "location": "London",
            "cuisine_type": "Italian",
            "description": "Italian restaurants in London"
        },
        {
            "location": "Paris",
            "rating_min": 4.0,
            "description": "High-rated restaurants in Paris"
        },
        {
            "location": "Tokyo",
            "price_range": "$$",
            "description": "Mid-price restaurants in Tokyo"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Location: {test_case['location']}")
        
        start_time = time.time()
        
        try:
            # Extract parameters
            location = test_case['location']
            cuisine_type = test_case.get('cuisine_type')
            price_range = test_case.get('price_range')
            rating_min = test_case.get('rating_min')
            
            # Call the search function
            result = search_restaurants(
                location=location,
                cuisine_type=cuisine_type,
                price_range=price_range,
                rating_min=rating_min
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Check if result contains expected content
            if "Error:" in result:
                print(f"❌ Error: {result}")
                success = False
            elif "restaurant" in result.lower() or "found" in result.lower():
                print(f"✅ Success: Found restaurants")
                print(f"   Response time: {response_time:.2f}s")
                success = True
            else:
                print(f"⚠️  Unexpected response: {result[:100]}...")
                success = False
            
            results.append({
                "test_number": i,
                "description": test_case['description'],
                "location": location,
                "cuisine_type": cuisine_type,
                "price_range": price_range,
                "rating_min": rating_min,
                "result": result,
                "response_time": response_time,
                "success": success
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "test_number": i,
                "description": test_case['description'],
                "location": test_case['location'],
                "result": f"Exception: {str(e)}",
                "response_time": time.time() - start_time,
                "success": False
            })
        
        # Add delay between tests
        if i < len(test_cases):
            time.sleep(2)
    
    return results

def test_search_restaurants_advanced():
    """Test advanced restaurant search with filters."""
    print("\nTesting Advanced Restaurant Search...")
    
    test_cases = [
        {
            "location": "San Francisco",
            "cuisine_type": "Chinese",
            "price_range": "$$$",
            "rating_min": 4.5,
            "description": "High-end Chinese restaurants in SF"
        },
        {
            "location": "Chicago",
            "cuisine_type": "Pizza",
            "price_range": "$",
            "description": "Budget pizza places in Chicago"
        },
        {
            "location": "Miami",
            "cuisine_type": "Seafood",
            "rating_min": 4.0,
            "description": "Well-rated seafood in Miami"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        
        start_time = time.time()
        
        try:
            result = search_restaurants(
                location=test_case['location'],
                cuisine_type=test_case.get('cuisine_type'),
                price_range=test_case.get('price_range'),
                rating_min=test_case.get('rating_min')
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if "Error:" in result:
                print(f"❌ Error: {result}")
                success = False
            else:
                print(f"✅ Success: {result[:100]}...")
                success = True
            
            results.append({
                "test_number": i,
                "description": test_case['description'],
                "result": result,
                "response_time": response_time,
                "success": success
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "test_number": i,
                "description": test_case['description'],
                "result": f"Exception: {str(e)}",
                "response_time": time.time() - start_time,
                "success": False
            })
        
        if i < len(test_cases):
            time.sleep(2)
    
    return results

def test_restaurant_details():
    """Test restaurant details functionality."""
    print("\nTesting Restaurant Details...")
    
    # First, search for a restaurant to get an ID
    print("Searching for a restaurant to get details...")
    
    try:
        search_result = search_restaurants("New York City")
        
        if "Error:" in search_result:
            print(f"❌ Cannot test restaurant details: {search_result}")
            return []
        
        # For this test, we'll simulate getting restaurant details
        # In a real scenario, you'd extract restaurant IDs from search results
        print("✅ Restaurant search successful - details test would work with actual restaurant IDs")
        
        # Test with a mock restaurant ID (this would fail but shows the structure)
        test_restaurant_id = "12345"  # Mock ID
        print(f"Testing with mock restaurant ID: {test_restaurant_id}")
        
        start_time = time.time()
        result = get_restaurant_details(test_restaurant_id)
        end_time = time.time()
        
        print(f"Result: {result}")
        print(f"Response time: {end_time - start_time:.2f}s")
        
        return [{
            "test_type": "restaurant_details",
            "restaurant_id": test_restaurant_id,
            "result": result,
            "response_time": end_time - start_time,
            "success": "Error:" not in result
        }]
        
    except Exception as e:
        print(f"❌ Exception in restaurant details test: {str(e)}")
        return [{
            "test_type": "restaurant_details",
            "result": f"Exception: {str(e)}",
            "success": False
        }]

def test_error_handling():
    """Test error handling scenarios."""
    print("\nTesting Error Handling...")
    
    test_cases = [
        {
            "location": "",
            "description": "Empty location"
        },
        {
            "location": "NonExistentCity12345",
            "description": "Non-existent city"
        },
        {
            "location": "New York",
            "rating_min": 6.0,  # Invalid rating
            "description": "Invalid rating"
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        
        try:
            result = search_restaurants(
                location=test_case['location'],
                rating_min=test_case.get('rating_min')
            )
            
            # Check if error is handled gracefully
            if "Error:" in result or "No restaurants found" in result:
                print(f"✅ Error handled gracefully: {result[:100]}...")
                success = True
            else:
                print(f"⚠️  Unexpected response: {result[:100]}...")
                success = False
            
            results.append({
                "test_number": i,
                "description": test_case['description'],
                "result": result,
                "success": success
            })
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            results.append({
                "test_number": i,
                "description": test_case['description'],
                "result": f"Exception: {str(e)}",
                "success": False
            })
        
        if i < len(test_cases):
            time.sleep(1)
    
    return results

def run_comprehensive_tripadvisor_tests():
    """Run comprehensive TripAdvisor API tests."""
    print("=" * 80)
    print("TRIPADVISOR API COMPREHENSIVE TESTS")
    print("=" * 80)
    
    # Ensure test data directory exists
    test_data_dir = ensure_test_data_dir()
    
    # Generate timestamp for file naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    all_results = {
        "test_run_timestamp": timestamp,
        "api_key_configured": bool(TRIPADVISOR_API_KEY),
        "test_categories": {},
        "summary": {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "total_response_time": 0
        }
    }
    
    # Test 1: API Connection
    print("\n1. Testing API Connection...")
    connection_success = test_tripadvisor_api_connection()
    all_results["api_connection"] = connection_success
    
    if not connection_success:
        print("❌ API connection failed. Skipping other tests.")
        return all_results
    
    # Test 2: Basic Restaurant Search
    print("\n2. Testing Basic Restaurant Search...")
    basic_results = test_search_restaurants_basic()
    all_results["test_categories"]["basic_search"] = {
        "tests": basic_results,
        "summary": {
            "total": len(basic_results),
            "successful": sum(1 for r in basic_results if r.get("success", False)),
            "failed": sum(1 for r in basic_results if not r.get("success", False)),
            "avg_response_time": sum(r.get("response_time", 0) for r in basic_results) / len(basic_results) if basic_results else 0
        }
    }
    
    # Test 3: Advanced Restaurant Search
    print("\n3. Testing Advanced Restaurant Search...")
    advanced_results = test_search_restaurants_advanced()
    all_results["test_categories"]["advanced_search"] = {
        "tests": advanced_results,
        "summary": {
            "total": len(advanced_results),
            "successful": sum(1 for r in advanced_results if r.get("success", False)),
            "failed": sum(1 for r in advanced_results if not r.get("success", False)),
            "avg_response_time": sum(r.get("response_time", 0) for r in advanced_results) / len(advanced_results) if advanced_results else 0
        }
    }
    
    # Test 4: Restaurant Details
    print("\n4. Testing Restaurant Details...")
    details_results = test_restaurant_details()
    all_results["test_categories"]["restaurant_details"] = {
        "tests": details_results,
        "summary": {
            "total": len(details_results),
            "successful": sum(1 for r in details_results if r.get("success", False)),
            "failed": sum(1 for r in details_results if not r.get("success", False)),
            "avg_response_time": sum(r.get("response_time", 0) for r in details_results) / len(details_results) if details_results else 0
        }
    }
    
    # Test 5: Error Handling
    print("\n5. Testing Error Handling...")
    error_results = test_error_handling()
    all_results["test_categories"]["error_handling"] = {
        "tests": error_results,
        "summary": {
            "total": len(error_results),
            "successful": sum(1 for r in error_results if r.get("success", False)),
            "failed": sum(1 for r in error_results if not r.get("success", False))
        }
    }
    
    # Calculate overall summary
    for category in all_results["test_categories"].values():
        all_results["summary"]["total_tests"] += category["summary"]["total"]
        all_results["summary"]["successful_tests"] += category["summary"]["successful"]
        all_results["summary"]["failed_tests"] += category["summary"]["failed"]
        all_results["summary"]["total_response_time"] += category["summary"].get("avg_response_time", 0) * category["summary"]["total"]
    
    if all_results["summary"]["total_tests"] > 0:
        all_results["summary"]["avg_response_time"] = (
            all_results["summary"]["total_response_time"] / all_results["summary"]["total_tests"]
        )
    
    # Save results
    results_filename = f"tripadvisor_api_test_results_{timestamp}.json"
    results_filepath = test_data_dir / results_filename
    
    with open(results_filepath, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    # Print final summary
    print("\n" + "="*80)
    print("TRIPADVISOR API TEST SUMMARY")
    print("="*80)
    print(f"API Key Configured: {'✅ Yes' if all_results['api_key_configured'] else '❌ No'}")
    print(f"API Connection: {'✅ Success' if all_results['api_connection'] else '❌ Failed'}")
    print(f"Total Tests: {all_results['summary']['total_tests']}")
    print(f"Successful: {all_results['summary']['successful_tests']}")
    print(f"Failed: {all_results['summary']['failed_tests']}")
    if all_results['summary']['total_tests'] > 0:
        success_rate = (all_results['summary']['successful_tests'] / all_results['summary']['total_tests']) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Average Response Time: {all_results['summary']['avg_response_time']:.2f} seconds")
    print(f"Results saved to: {results_filepath}")
    
    return all_results

def run_quick_tripadvisor_tests():
    """Run quick TripAdvisor API tests."""
    print("=" * 60)
    print("TRIPADVISOR API QUICK TESTS")
    print("=" * 60)
    
    # Test API connection
    print("\n1. Testing API Connection...")
    connection_success = test_tripadvisor_api_connection()
    
    if not connection_success:
        print("❌ API connection failed. Cannot run other tests.")
        return
    
    # Test basic search
    print("\n2. Testing Basic Restaurant Search...")
    basic_results = test_search_restaurants_basic()
    
    # Test error handling
    print("\n3. Testing Error Handling...")
    error_results = test_error_handling()
    
    print("\n" + "="*60)
    print("QUICK TEST SUMMARY")
    print("="*60)
    print(f"API Connection: {'✅ Success' if connection_success else '❌ Failed'}")
    print(f"Basic Search Tests: {len(basic_results)}")
    print(f"Error Handling Tests: {len(error_results)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Run quick tests
        run_quick_tripadvisor_tests()
    else:
        # Run comprehensive tests by default
        run_comprehensive_tripadvisor_tests() 