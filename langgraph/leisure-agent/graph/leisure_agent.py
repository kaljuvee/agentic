from typing import Literal, Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
import requests
import csv
import io
import json
from typing import List, Dict, Any

#https://github.com/langchain-ai/langgraph/blob/main/docs/docs/concepts/low_level.md
# Load environment variables
load_dotenv()

# Define the state type
class OpenFlightsState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: Optional[str]

# OpenFlights API base URLs
OPENFLIGHTS_BASE_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data"
AIRPORTS_URL = f"{OPENFLIGHTS_BASE_URL}/airports.dat"
AIRLINES_URL = f"{OPENFLIGHTS_BASE_URL}/airlines.dat"
ROUTES_URL = f"{OPENFLIGHTS_BASE_URL}/routes.dat"

# TripAdvisor API configuration
TRIPADVISOR_API_KEY = os.getenv("TRIPADVISOR_API_KEY")
TRIPADVISOR_BASE_URL = "https://api.content.tripadvisor.com/api/v1"

def fetch_csv_data(url: str) -> List[List[str]]:
    """Fetch CSV data from OpenFlights repository."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse CSV data
        csv_data = []
        csv_reader = csv.reader(io.StringIO(response.text))
        for row in csv_reader:
            csv_data.append(row)
        return csv_data
    except Exception as e:
        print(f"Error fetching data from {url}: {str(e)}")
        return []

@tool
def search_airports(query: str, country: Optional[str] = None) -> str:
    """
    Search for airports by name, IATA code, or ICAO code.
    Parameters:
        query: Search term (airport name, IATA code, or ICAO code)
        country: Optional country filter
    """
    try:
        airports_data = fetch_csv_data(AIRPORTS_URL)
        if not airports_data:
            return "Error: Unable to fetch airports data."
        
        # OpenFlights airports.dat format:
        # 0: Airport ID, 1: Name, 2: City, 3: Country, 4: IATA, 5: ICAO, 6: Latitude, 7: Longitude, 8: Altitude, 9: Timezone, 10: DST, 11: Tz database time zone, 12: Type, 13: Source
        
        results = []
        query_lower = query.lower()
        
        for airport in airports_data:
            if len(airport) < 14:
                continue
                
            airport_name = airport[1].lower()
            iata_code = airport[4].lower()
            icao_code = airport[5].lower()
            country_name = airport[3].lower()
            
            # Check if query matches any field
            if (query_lower in airport_name or 
                query_lower in iata_code or 
                query_lower in icao_code):
                
                # Apply country filter if provided
                if country and country.lower() not in country_name:
                    continue
                    
                results.append({
                    'name': airport[1],
                    'city': airport[2],
                    'country': airport[3],
                    'iata': airport[4],
                    'icao': airport[5],
                    'latitude': airport[6],
                    'longitude': airport[7],
                    'timezone': airport[9]
                })
                
                # Limit results to avoid overwhelming response
                if len(results) >= 10:
                    break
        
        if not results:
            return f"No airports found matching '{query}'"
        
        response = f"Found {len(results)} airport(s) matching '{query}':\n\n"
        for i, airport in enumerate(results, 1):
            response += (
                f"{i}. {airport['name']} ({airport['iata']}/{airport['icao']})\n"
                f"   City: {airport['city']}, {airport['country']}\n"
                f"   Coordinates: {airport['latitude']}, {airport['longitude']}\n"
                f"   Timezone: {airport['timezone']}\n\n"
            )
        
        return response
        
    except Exception as e:
        return f"Error searching airports: {str(e)}"

@tool
def search_airlines(query: str, country: Optional[str] = None) -> str:
    """
    Search for airlines by name, IATA code, or ICAO code.
    Parameters:
        query: Search term (airline name, IATA code, or ICAO code)
        country: Optional country filter
    """
    try:
        airlines_data = fetch_csv_data(AIRLINES_URL)
        if not airlines_data:
            return "Error: Unable to fetch airlines data."
        
        # OpenFlights airlines.dat format:
        # 0: Airline ID, 1: Name, 2: Alias, 3: IATA, 4: ICAO, 5: Callsign, 6: Country, 7: Active
        
        results = []
        query_lower = query.lower()
        
        for airline in airlines_data:
            if len(airline) < 8:
                continue
                
            airline_name = airline[1].lower()
            iata_code = airline[3].lower()
            icao_code = airline[4].lower()
            country_name = airline[6].lower()
            
            # Check if query matches any field
            if (query_lower in airline_name or 
                query_lower in iata_code or 
                query_lower in icao_code):
                
                # Apply country filter if provided
                if country and country.lower() not in country_name:
                    continue
                    
                results.append({
                    'name': airline[1],
                    'alias': airline[2],
                    'iata': airline[3],
                    'icao': airline[4],
                    'callsign': airline[5],
                    'country': airline[6],
                    'active': airline[7]
                })
                
                # Limit results
                if len(results) >= 10:
                    break
        
        if not results:
            return f"No airlines found matching '{query}'"
        
        response = f"Found {len(results)} airline(s) matching '{query}':\n\n"
        for i, airline in enumerate(results, 1):
            status = "Active" if airline['active'] == 'Y' else "Inactive"
            response += (
                f"{i}. {airline['name']} ({airline['iata']}/{airline['icao']})\n"
                f"   Country: {airline['country']}\n"
                f"   Callsign: {airline['callsign']}\n"
                f"   Status: {status}\n\n"
            )
        
        return response
        
    except Exception as e:
        return f"Error searching airlines: {str(e)}"

@tool
def find_routes(origin: str, destination: str, airline: Optional[str] = None) -> str:
    """
    Find routes between airports.
    Parameters:
        origin: Origin airport (IATA code, ICAO code, or name)
        destination: Destination airport (IATA code, ICAO code, or name)
        airline: Optional airline filter (IATA code, ICAO code, or name)
    """
    try:
        routes_data = fetch_csv_data(ROUTES_URL)
        if not routes_data:
            return "Error: Unable to fetch routes data."
        
        # OpenFlights routes.dat format:
        # 0: Airline, 1: Airline ID, 2: Source airport, 3: Source airport ID, 4: Destination airport, 5: Destination airport ID, 6: Codeshare, 7: Stops, 8: Equipment
        
        # First, get airport data to resolve names to codes
        airports_data = fetch_csv_data(AIRPORTS_URL)
        airport_code_map = {}
        
        for airport in airports_data:
            if len(airport) >= 6:
                airport_code_map[airport[1].lower()] = airport[4]  # name to IATA
                airport_code_map[airport[4].lower()] = airport[4]  # IATA to IATA
                airport_code_map[airport[5].lower()] = airport[4]  # ICAO to IATA
        
        # Resolve origin and destination to IATA codes
        origin_iata = airport_code_map.get(origin.lower(), origin.upper())
        dest_iata = airport_code_map.get(destination.lower(), destination.upper())
        
        results = []
        
        for route in routes_data:
            if len(route) < 9:
                continue
                
            route_airline = route[0]
            source_airport = route[2]
            dest_airport = route[4]
            stops = route[7]
            equipment = route[8]
            
            # Check if route matches origin and destination
            if (source_airport == origin_iata and dest_airport == dest_iata):
                
                # Apply airline filter if provided
                if airline and airline.lower() not in route_airline.lower():
                    continue
                    
                results.append({
                    'airline': route_airline,
                    'source': source_airport,
                    'destination': dest_airport,
                    'stops': stops,
                    'equipment': equipment,
                    'codeshare': route[6] if len(route) > 6 else 'N'
                })
                
                # Limit results
                if len(results) >= 15:
                    break
        
        if not results:
            return f"No routes found from {origin} to {destination}"
        
        response = f"Found {len(results)} route(s) from {origin} to {destination}:\n\n"
        for i, route in enumerate(results, 1):
            codeshare = "Yes" if route['codeshare'] == 'Y' else "No"
            response += (
                f"{i}. {route['airline']}\n"
                f"   Route: {route['source']} → {route['destination']}\n"
                f"   Stops: {route['stops']}\n"
                f"   Equipment: {route['equipment']}\n"
                f"   Codeshare: {codeshare}\n\n"
            )
        
        return response
        
    except Exception as e:
        return f"Error finding routes: {str(e)}"

@tool
def get_airport_info(iata_code: str) -> str:
    """
    Get detailed information about a specific airport by IATA code.
    Parameters:
        iata_code: The IATA code of the airport (e.g., 'JFK', 'LAX')
    """
    try:
        airports_data = fetch_csv_data(AIRPORTS_URL)
        if not airports_data:
            return "Error: Unable to fetch airports data."
        
        iata_code_upper = iata_code.upper()
        
        for airport in airports_data:
            if len(airport) < 14:
                continue
                
            if airport[4] == iata_code_upper:
                return (
                    f"Airport Information for {iata_code_upper}:\n\n"
                    f"Name: {airport[1]}\n"
                    f"City: {airport[2]}\n"
                    f"Country: {airport[3]}\n"
                    f"IATA Code: {airport[4]}\n"
                    f"ICAO Code: {airport[5]}\n"
                    f"Coordinates: {airport[6]}, {airport[7]}\n"
                    f"Altitude: {airport[8]} feet\n"
                    f"Timezone: {airport[9]}\n"
                    f"DST: {airport[10]}\n"
                    f"Tz Database: {airport[11]}\n"
                    f"Type: {airport[12]}\n"
                    f"Source: {airport[13]}"
                )
        
        return f"No airport found with IATA code '{iata_code}'"
        
    except Exception as e:
        return f"Error getting airport info: {str(e)}"

@tool
def get_airline_info(iata_code: str) -> str:
    """
    Get detailed information about a specific airline by IATA code.
    Parameters:
        iata_code: The IATA code of the airline (e.g., 'AA', 'UA')
    """
    try:
        airlines_data = fetch_csv_data(AIRLINES_URL)
        if not airlines_data:
            return "Error: Unable to fetch airlines data."
        
        iata_code_upper = iata_code.upper()
        
        for airline in airlines_data:
            if len(airline) < 8:
                continue
                
            if airline[3] == iata_code_upper:
                status = "Active" if airline[7] == 'Y' else "Inactive"
                return (
                    f"Airline Information for {iata_code_upper}:\n\n"
                    f"Name: {airline[1]}\n"
                    f"Alias: {airline[2]}\n"
                    f"IATA Code: {airline[3]}\n"
                    f"ICAO Code: {airline[4]}\n"
                    f"Callsign: {airline[5]}\n"
                    f"Country: {airline[6]}\n"
                    f"Status: {status}"
                )
        
        return f"No airline found with IATA code '{iata_code}'"
        
    except Exception as e:
        return f"Error getting airline info: {str(e)}"

@tool
def search_restaurants(location: str, cuisine_type: Optional[str] = None, price_range: Optional[str] = None, rating_min: Optional[float] = None) -> str:
    """
    Search for restaurants in a specific location using TripAdvisor API.
    Parameters:
        location: City, address, or location to search for restaurants
        cuisine_type: Optional cuisine type filter (e.g., 'Italian', 'Chinese', 'Mexican')
        price_range: Optional price range filter ('$', '$$', '$$$', '$$$$')
        rating_min: Optional minimum rating filter (1.0 to 5.0)
    """
    try:
        if not TRIPADVISOR_API_KEY:
            return "Error: TripAdvisor API key not configured. Please set TRIPADVISOR_API_KEY environment variable."
        
        # Search for location first to get location_id
        location_url = f"{TRIPADVISOR_BASE_URL}/location/search"
        location_params = {
            'key': TRIPADVISOR_API_KEY,
            'searchQuery': location,
            'category': 'restaurants',
            'language': 'en'
        }
        
        location_response = requests.get(location_url, params=location_params)
        location_response.raise_for_status()
        location_data = location_response.json()
        
        if not location_data.get('data'):
            return f"No locations found for '{location}'"
        
        # Use the first location found
        location_id = location_data['data'][0]['location_id']
        
        # Search for restaurants in the location
        restaurants_url = f"{TRIPADVISOR_BASE_URL}/location/{location_id}/restaurants"
        restaurant_params = {
            'key': TRIPADVISOR_API_KEY,
            'language': 'en',
            'limit': 20
        }
        
        # Add optional filters
        if cuisine_type:
            restaurant_params['cuisine'] = cuisine_type
        if price_range:
            restaurant_params['price'] = price_range
        if rating_min:
            restaurant_params['min_rating'] = rating_min
        
        restaurant_response = requests.get(restaurants_url, params=restaurant_params)
        restaurant_response.raise_for_status()
        restaurant_data = restaurant_response.json()
        
        if not restaurant_data.get('data'):
            return f"No restaurants found in {location}"
        
        restaurants = restaurant_data['data']
        
        # Format the response
        response = f"Found {len(restaurants)} restaurant(s) in {location}:\n\n"
        
        for i, restaurant in enumerate(restaurants[:10], 1):  # Limit to 10 results
            name = restaurant.get('name', 'Unknown')
            rating = restaurant.get('rating', 'No rating')
            price_level = restaurant.get('price_level', '')
            cuisine = restaurant.get('cuisine', [])
            address = restaurant.get('address_string', 'Address not available')
            
            # Format cuisine list
            cuisine_str = ', '.join(cuisine) if cuisine else 'Cuisine not specified'
            
            # Format price level
            price_display = '💰' * len(price_level) if price_level else 'Price not available'
            
            response += (
                f"{i}. {name}\n"
                f"   Rating: {rating}/5.0 ⭐\n"
                f"   Price: {price_display}\n"
                f"   Cuisine: {cuisine_str}\n"
                f"   Address: {address}\n\n"
            )
        
        return response
        
    except requests.exceptions.RequestException as e:
        return f"Error accessing TripAdvisor API: {str(e)}"
    except Exception as e:
        return f"Error searching restaurants: {str(e)}"

@tool
def get_restaurant_details(restaurant_id: str) -> str:
    """
    Get detailed information about a specific restaurant using TripAdvisor API.
    Parameters:
        restaurant_id: The TripAdvisor restaurant ID
    """
    try:
        if not TRIPADVISOR_API_KEY:
            return "Error: TripAdvisor API key not configured. Please set TRIPADVISOR_API_KEY environment variable."
        
        # Get restaurant details
        details_url = f"{TRIPADVISOR_BASE_URL}/location/{restaurant_id}/details"
        params = {
            'key': TRIPADVISOR_API_KEY,
            'language': 'en'
        }
        
        response = requests.get(details_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data:
            return f"No restaurant found with ID '{restaurant_id}'"
        
        restaurant = data
        
        # Format detailed information
        name = restaurant.get('name', 'Unknown')
        rating = restaurant.get('rating', 'No rating')
        price_level = restaurant.get('price_level', '')
        cuisine = restaurant.get('cuisine', [])
        address = restaurant.get('address_string', 'Address not available')
        phone = restaurant.get('phone', 'Phone not available')
        website = restaurant.get('website', 'Website not available')
        hours = restaurant.get('hours', {})
        description = restaurant.get('description', 'No description available')
        
        # Format cuisine list
        cuisine_str = ', '.join(cuisine) if cuisine else 'Cuisine not specified'
        
        # Format price level
        price_display = '💰' * len(price_level) if price_level else 'Price not available'
        
        # Format hours
        hours_str = "Hours not available"
        if hours:
            hours_list = []
            for day, time_range in hours.items():
                hours_list.append(f"{day}: {time_range}")
            hours_str = '\n   '.join(hours_list)
        
        response = (
            f"Restaurant Details for {name}:\n\n"
            f"Rating: {rating}/5.0 ⭐\n"
            f"Price Level: {price_display}\n"
            f"Cuisine: {cuisine_str}\n"
            f"Address: {address}\n"
            f"Phone: {phone}\n"
            f"Website: {website}\n\n"
            f"Hours:\n   {hours_str}\n\n"
            f"Description: {description}"
        )
        
        return response
        
    except requests.exceptions.RequestException as e:
        return f"Error accessing TripAdvisor API: {str(e)}"
    except Exception as e:
        return f"Error getting restaurant details: {str(e)}"

# Initialize tools
tools = [search_airports, search_airlines, find_routes, get_airport_info, get_airline_info, search_restaurants, get_restaurant_details]

# Initialize the model with a specific prompt
system_prompt = """You are a professional travel and dining information assistant powered by OpenFlights data and TripAdvisor API. Your task is to help users find information about airports, airlines, flight routes, and restaurants worldwide.

You have access to the following tools:
1. search_airports: Search for airports by name, IATA code, or ICAO code
2. search_airlines: Search for airlines by name, IATA code, or ICAO code
3. find_routes: Find routes between airports
4. get_airport_info: Get detailed information about a specific airport
5. get_airline_info: Get detailed information about a specific airline
6. search_restaurants: Search for restaurants in a specific location
7. get_restaurant_details: Get detailed information about a specific restaurant

When helping users:
1. Always provide clear and accurate information
2. Use IATA codes when possible for precision
3. Explain any limitations of the data
4. Be helpful with travel planning queries
5. Provide context about airports, airlines, and restaurants when relevant
6. For restaurant queries, consider cuisine preferences, price ranges, and ratings
7. Help users find dining options that match their preferences and budget

Remember to:
1. Be precise with airport and airline codes
2. Explain timezone information when relevant
3. Maintain a helpful and professional tone
4. Clarify any ambiguous requests
5. Note that this is reference data, not real-time booking information
6. For restaurants, provide helpful recommendations based on location and preferences
7. Include price levels and ratings when available for restaurant suggestions
"""

# Initialize the model
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
    temperature=0.7,
    streaming=True,
    openai_api_key=os.getenv("OPENAI_API_KEY")
).bind_tools(tools)

# Create tool node
tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Determine if we should continue using tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: OpenFlightsState):
    """Call the model with the current state."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Create and configure the graph
def create_graph():
    """Create and configure the LangGraph for the OpenFlights agent."""
    # Create the graph
    workflow = StateGraph(OpenFlightsState)
    
    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "agent")
    
    # Initialize memory
    checkpointer = MemorySaver()
    
    # Compile the graph
    return workflow.compile(checkpointer=checkpointer)

# Create the graph
graph = create_graph()

# Define the output nodes
output_nodes = ["agent"]

async def stream_response(
    question: str,
    thread_id: str = "openflights_demo"
) -> str:
    """
    Stream a response from the OpenFlights agent for a given question.
    
    Args:
        question (str): The user's travel-related question
        thread_id (str): Thread identifier for the conversation
        
    Returns:
        An async generator that yields streaming responses
    """
    state = {
        "messages": [{"role": "user", "content": question}],
        "thread_id": thread_id
    }
    
    async for stream_mode, chunk in graph.astream(
        state, 
        stream_mode=["messages"],
        config={"configurable": {"thread_id": thread_id}}
    ):
        if stream_mode == "messages":
            msg, metadata = chunk
            if msg.content and metadata["langgraph_node"] in output_nodes:
                yield f"data: {msg.content}\n\n"

def get_response(
    question: str,
    thread_id: str = "openflights_demo"
) -> dict:
    """
    Get a response from the OpenFlights agent for a given question.
    
    Args:
        question (str): The user's travel-related question
        thread_id (str): Thread identifier for the conversation
        
    Returns:
        dict: The final state containing the conversation
    """
    initial_message = {
        "messages": [{
            "role": "user",
            "content": question
        }],
        "thread_id": thread_id
    }
    
    return graph.invoke(
        initial_message,
        config={"configurable": {"thread_id": thread_id}}
    )

if __name__ == "__main__":
    # Test the agent directly
    question = "What airports are available in New York?"
    final_state = get_response(question)
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")