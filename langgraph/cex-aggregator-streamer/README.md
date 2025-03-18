# Cryptocurrency Exchange (CEX) Aggregator

A cryptocurrency exchange aggregator agent that allows you to query information from multiple exchanges and compare prices across platforms.

Uses LangGraph and demonstrates concepts like:
- Structured LLM output
- Custom graph state management
- Custom graph output streaming
- Prompt construction
- Tool use
- Integration with CCXT library for cryptocurrency exchange access

## Capabilities

- **Multi-Exchange Support**: Connect to multiple cryptocurrency exchanges through a single interface
- **Tool Use**: Agent has access to various exchange-related tools:
  - `get_exchange_list`: List all available exchanges
  - `get_balance`: Check account balance on a specific exchange
  - `get_ticker`: Get current price and information for a trading pair
  - `get_markets`: View available markets/trading pairs on an exchange
  - `get_order_book`: View current buy and sell orders for a trading pair
  - `compare_prices`: Compare prices for a trading pair across multiple exchanges
- **Streaming Responses**: Get real-time streaming responses from the agent
- **Conversation Memory**: Maintain conversation context with thread IDs
- **Standardized API**: Follows the standardized schema for all chat endpoints

## Example Usage

**User**
_"What exchanges are available?"_
_"Show me my balance on Binance"_
_"What is the price of BTC/USDT on Bybit?"_
_"Compare Bitcoin prices across all exchanges"_

**CEX Aggregator Agent**
_Queries exchange information and returns formatted responses in real-time_

## Running Locally

Create a `.env` file to store your environment variables based on the provided `.env.sample`. Do not commit this file to the repository.

```bash
# OpenAI API Configuration
OPENAI_MODEL_NAME='gpt-4o-mini'
OPENAI_API_KEY='your-openai-api-key-here'

# Exchange API Keys (add your actual keys)
# Bitstamp
BITSTAMP_API_KEY='your-bitstamp-api-key-here'
BITSTAMP_SECRET='your-bitstamp-secret-here'
BITSTAMP_UID='your-bitstamp-uid-here'

# Binance
BINANCE_API_KEY='your-binance-api-key-here'
BINANCE_SECRET='your-binance-secret-here'

# Additional exchanges...
```

### With Docker

```bash
docker build -t cex-aggregator .
docker run -p 8000:8000 cex-aggregator
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn run:app --reload
```

### Testing the Agent

You can test the agent using the provided test script which automatically runs a series of predefined exchange queries:

```bash
python tests/cex_aggregator_test.py
```

The test script will run the following queries:
- "What exchanges are available?"
- "Show me my balance on Binance"
- "What is the price of BTC/USDT on Bybit?"

## API Endpoints

- `/chat`: CEX aggregator agent endpoint

The endpoint accepts POST requests with the following JSON structure:
```json
{
  "input": "Your cryptocurrency exchange question or command",
  "history": [
    {
      "role": "user",
      "content": "Previous user message"
    },
    {
      "role": "agent",
      "content": "Previous agent response"
    }
  ],
  "config": {
    "thread_id": "unique_conversation_id",
    "streaming": true
  }
}
```

### Request Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | string | Required. The current user message or query |
| `history` | array | Optional. List of previous messages in the conversation |
| `config` | object | Optional. Configuration options for the agent |

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `thread_id` | string | "cex_demo" | Unique identifier for the conversation thread |
| `streaming` | boolean | true | Whether to return a streaming response |

## Project Structure

- `graph/cex_aggregator.py`: Contains the CEX aggregator agent implementation with LangGraph
- `graph/exchange_factory.py`: Factory for initializing exchange clients
- `run.py`: FastAPI server that exposes the agent as an endpoint
- `tests/cex_aggregator_test.py`: Test script for the CEX aggregator agent

## Supported Exchanges

The agent currently supports the following exchanges:
- Binance
- Bitstamp
- Kraken
- Poloniex
- Bybit
- OKX

## Future Enhancements

- Add support for more exchanges
- Implement trading functionality (place orders, cancel orders)
- Add historical price data and charting capabilities
- Implement arbitrage opportunity detection
- Add portfolio tracking and performance analysis
- Support for more complex trading strategies
- Enhanced security features for API key management
