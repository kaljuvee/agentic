# Alpaca Trader

A trade execution agent that allows you to query account information and execute trades via Alpaca Markets API.

Uses LangGraph and demonstrates concepts like:
- Structured LLM output
- Custom graph state management
- Custom graph output streaming
- Prompt construction
- Tool use
- FastAPI integration for real-time streaming responses

## Capabilities

- **Tool Use**: Agent has access to Alpaca Markets API tools:
  - `get_account_info`: Check account balance and status
  - `get_assets`: View available assets for trading
  - `place_market_order`: Place market orders
  - `get_positions`: View current positions
- **Streaming Responses**: Get real-time streaming responses from the agent
- **Conversation Memory**: Maintain conversation context with thread IDs

## Example Usage

**User**
_"Show me my account information."_
_"Place a market order to buy 1 share of AAPL"_
_"What positions do I currently have?"_

**Alpaca Agent**
_Queries account info or executes trades in real-time_

## Running Locally

Create a `.env` file to store your environment variables. Do not commit this file to the repository.

```bash
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL_NAME=gpt-4o
ALPACA_PAPER_API_KEY=your_alpaca_paper_api_key
ALPACA_PAPER_SECRET_KEY=your_alpaca_paper_secret_key
```

### With Docker

```bash
docker build -t alpaca-agent .
docker run -p 8000:8000 alpaca-agent
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn run:app --reload
```

### Testing the Agent

You can test the agent using the provided test script which automatically runs a series of predefined trading queries:

```bash
python tests/alpaca_agent_test.py
```

The test script will run the following queries:
- "Show me my account information"
- "Show me my current positions"
- "Place a market order to buy 1 share of INTL"

## API Endpoints

- `/chat`: Trading agent endpoint

The endpoint accepts POST requests with the following JSON structure:
```json
{
  "input": "Your trading question or command",
  "userId": "unique_user_id",
  "messageHistory": []
}
```

## Project Structure

- `graph/alpaca_nodes.py`: Contains the trading tools and model definitions
- `graph/alpaca_graph.py`: Defines the LangGraph for the trading agent
- `graph/types.py`: Contains the state definitions for the agent
- `run.py`: FastAPI server that exposes the agent as an endpoint
- `tests/alpaca_agent_test.py`: Test script for the trading agent

## Future Enhancements

- Introduce "decision nodes" which allow the user to cancel and modify orders
- Allow the user to save trade ideas and continue later
- Add more modalities to the input and output (audio, etc.)
- Thread-level and cross-thread memory
- Support for more complex trading strategies
- Historical performance tracking
