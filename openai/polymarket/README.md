# Polymarket Analysis Agent

A sophisticated AI-powered analysis agent for Polymarket prediction markets that fetches comprehensive market data, provides insightful analysis, and helps users understand market probabilities.

## Features

- **Comprehensive Market Data Retrieval**: Fetches all active and open markets from Polymarket with efficient pagination
- **Smart Market Filtering**: Filter markets by keywords, categories, or find the most recent market
- **Market Summaries**: Generate detailed breakdowns of markets by category with upcoming events
- **Detailed Market Analysis**: Provides comprehensive details about specific markets including prices, volumes, and liquidity
- **Web-based Research**: Uses AI to search and analyze news to provide context for market probabilities
- **Interactive API**: Provides a streaming API endpoint for real-time interaction through natural language
- **OpenAI Agent Integration**: Leverages the OpenAI Agents SDK for advanced reasoning and explanation

## Prerequisites

- Python 3.9+
- FastAPI
- OpenAI Agents SDK
- Polymarket `py_clob_client`
- Valid Polymarket API key or private key
- OpenAI API key

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/polymarket-agent.git
cd polymarket-agent
```

2. Set up a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root with the following variables:

```
# Option 1: Use Polymarket private key
POLYMARKET_PRIVATE_KEY=your_polymarket_private_key

# Option 2: Use API credentials
POLYMARKET_API_KEY=your_api_key
POLYMARKET_API_SECRET=your_api_secret
POLYMARKET_API_PASSPHRASE=your_api_passphrase

# Required for OpenAI agent
OPENAI_API_KEY=your_openai_api_key

# Optional settings
POLYMARKET_HOST=https://clob.polymarket.com  # Default CLOB API endpoint
CHAIN_ID=137  # Default chain ID for Polygon
MAX_ORDER_SIZE=100  # Maximum order size for safety
```

2. If using a private key, ensure you have proper token allowances set up for the Polymarket CLOB client (one-time setup):

```python
from py_clob_client.client import ClobClient
client = ClobClient("https://clob.polymarket.com", chain_id=137, key="your_private_key")
client.set_token_allowance("USDC_TOKEN_ADDRESS", amount_in_wei)
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   Create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your-key-here
   OPENAI_MODEL=gpt-4o-mini
   ```

3. **Run the FastAPI service**:
   ```bash
   uvicorn main:app --reload
   ```
   This will start the service at `http://localhost:8000`.

## Testing the API

You can test the `/chat` endpoint using curl:

```bash
# Test agent capabilities
curl -X POST "https://zuvu-polymarket-agent.fly.dev/chat" \
     -H "Content-Type: application/json" \
     -d '{"input": "What can you help me with?"}'

# Get general market overview
curl -X POST "https://zuvu-polymarket-agent.fly.dev/chat" \
     -H "Content-Type: application/json" \
     -d '{"input": "What markets are available on Polymarket right now?"}'

# Search for specific market types
curl -X POST "https://zuvu-polymarket-agent.fly.dev/chat" \
     -H "Content-Type: application/json" \
     -d '{"input": "Tell me about upcoming election markets"}'

# Check service health
curl "https://zuvu-polymarket-agent.fly.dev/health"
```

For local development, replace the URL with `http://localhost:8000`:

```bash
# Local testing
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"input": "What are the most active markets right now?"}'
```

## Running Tests

To run the test script for the agent:
```bash
python tests/polymarket_agent_test.py
```

To run the API tests:
```bash
python tests/api_test.py
```

## Usage

1. Start the server:

```bash
uvicorn main:app --reload
```

2. Send queries to the agent:

```bash
# General market overview
curl -X POST "http://localhost:8000/chat" \
-H "Content-Type: application/json" \
-d '{"input": "What markets are available on Polymarket right now?"}' \
--no-buffer

# Category-specific markets
curl -X POST "http://localhost:8000/chat" \
-H "Content-Type: application/json" \
-d '{"input": "Tell me about upcoming election markets"}' \
--no-buffer

# Specific market analysis
curl -X POST "http://localhost:8000/chat" \
-H "Content-Type: application/json" \
-d '{"input": "Analyze the current Trump vs Biden election market"}' \
--no-buffer
```

3. The agent will:
   - Fetch relevant Polymarket markets based on your query
   - Provide detailed information about the markets
   - Search for relevant news if analyzing specific markets
   - Explain how to interpret the market probabilities
   - Offer insights about factors that might affect the outcomes

## Architecture

### Components

- **FastAPI Server**: Handles HTTP requests and streaming responses
- **OpenAI Agent**: Processes user inputs and orchestrates the market analysis
- **Market Analysis Tools**:
  - `get_active_open_markets`: Lists markets with optional keyword filtering
  - `get_market_details`: Provides detailed info for a specific market
  - `get_most_recent_market`: Finds the newest market available
  - `get_market_summary`: Generates category-based summary of all markets
  - `place_limit_order`: Executes trades (when authorized)
- **Web Search**: Gathers current news for market context
- **Streaming Response**: Returns agent thoughts and actions in real-time

### Flow

1. User submits a query about Polymarket markets
2. Agent determines the appropriate tool(s) to use
3. Agent fetches relevant market data
4. For specific markets, agent searches for relevant news
5. Agent interprets the market data and provides context
6. Agent explains the probabilities and what they represent
7. Results stream back to the user in real-time

## Graceful Degradation

The system is designed to handle failures gracefully:
- If the Polymarket API returns unexpected data, the agent reports the issue clearly
- Pagination ensures complete market retrieval even with large datasets
- All exceptions are captured and returned as readable messages

## License

MIT License

## Disclaimer

This tool is for educational purposes only. Trading on prediction markets involves risk. Always conduct your own research before making financial decisions. 