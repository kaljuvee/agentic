# OpenFlights Travel Agent

A travel information agent that provides comprehensive data about airports, airlines, and flight routes worldwide using the OpenFlights database.

Uses LangGraph and demonstrates concepts like:
- Structured LLM output
- Custom graph state management
- Custom graph output streaming
- Prompt construction
- Tool use
- FastAPI integration for real-time streaming responses

## Capabilities

- **Tool Use**: Agent has access to OpenFlights data tools:
  - `search_airports`: Search for airports by name, IATA code, or ICAO code
  - `search_airlines`: Search for airlines by name, IATA code, or ICAO code
  - `find_routes`: Find routes between airports
  - `get_airport_info`: Get detailed information about a specific airport
  - `get_airline_info`: Get detailed information about a specific airline
- **Streaming Responses**: Get real-time streaming responses from the agent
- **Conversation Memory**: Maintain conversation context with thread IDs
- **Comprehensive Data**: Access to worldwide airport, airline, and route information

## Example Usage

**User**
_"What airports are available in New York?"_
_"Show me routes from JFK to LAX"_
_"What airlines operate in the United States?"_
_"Give me information about American Airlines"_

**OpenFlights Agent**
_Provides detailed airport, airline, and route information from the OpenFlights database_

## Data Sources

The agent uses the OpenFlights database, which provides:
- **Airports**: Over 10,000 airports worldwide with IATA/ICAO codes, coordinates, and timezone information
- **Airlines**: Comprehensive airline data including active/inactive status
- **Routes**: Flight routes between airports with equipment and codeshare information

## Running Locally

Create a `.env` file to store your environment variables. Do not commit this file to the repository.

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o
```

### With Docker

```bash
docker build -t openflights-agent .
docker run -p 8000:8000 openflights-agent
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:<path-to-dir>/agentic/langgraph/travel-agent
uvicorn run:app --reload
```

### Testing the Agent

You can test the agent using the provided test script which automatically runs a series of predefined travel queries:

```bash
python tests/travel_agent_test.py
```

The test script will run the following queries:
- "What airports are available in New York?"
- "Show me information about JFK airport"
- "Find routes from JFK to LAX"

## API Endpoints

- `/chat`: Travel agent endpoint

The endpoint accepts POST requests with the following JSON structure:
```json
{
  "input": "Your travel question or query",
  "userId": "unique_user_id",
  "messageHistory": []
}
```

## Project Structure

- `graph/travel_agent.py`: Contains the OpenFlights tools and model definitions
- `run.py`: FastAPI server that exposes the agent as an endpoint
- `tests/travel_agent_test.py`: Test script for the travel agent

## Features

### Airport Information
- Search by name, IATA code, or ICAO code
- Filter by country
- Detailed information including coordinates, timezone, and altitude
- Support for major and regional airports worldwide

### Airline Information
- Search by name, IATA code, or ICAO code
- Filter by country
- Active/inactive status information
- Callsign and alias data

### Route Information
- Find routes between any two airports
- Filter by specific airlines
- Equipment and codeshare information
- Stop information (direct vs connecting flights)

## Limitations

- **Static Data**: The OpenFlights database is updated periodically but not in real-time
- **No Booking**: This is reference data only - no actual flight booking capabilities
- **No Pricing**: No fare or pricing information available
- **Historical Routes**: Some routes may be historical and no longer active

## Future Enhancements

- Add support for ferry terminals and railway stations (multimodal transport)
- Implement caching for frequently accessed data
- Add distance calculations between airports
- Support for flight time estimates
- Integration with real-time flight status APIs
- Add support for airport facilities and services information
- Implement geolocation-based airport search

## Data Attribution

This agent uses data from the OpenFlights database, which is open-source and freely available. For more information, visit: https://openflights.org/data.html
