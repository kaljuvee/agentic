### Detailed Guide on Interacting with Polymarket via CLOB API

Polymarket is a decentralized prediction market platform that allows users to bet on the outcomes of real-world events using cryptocurrency, primarily USDC, on the Polygon blockchain network. The Central Limit Order Book (CLOB) API provides programmatic access to Polymarket's hybrid-decentralized trading system, enabling users to create, manage, and analyze orders efficiently. This guide explains how to interact with Polymarket via its CLOB API, covering setup, authentication, order management, and market data access.

---

## Overview of Polymarket and CLOB
Polymarket enables speculation on events like elections or economic indicators using a hybrid-decentralized Central Limit Order Book (CLOB), also called the "Binary Limit Order Book" (BLOB). In this system:
- **Off-chain Operators**: Handle order matching for efficiency.
- **On-chain Smart Contracts**: Ensure non-custodial settlement, maintaining security and transparency.

The CLOB API supports:
- **REST Endpoint**: `https://clob.polymarket.com/`
- **Websocket Endpoint**: `wss://ws-subscriptions-clob.polymarket.com/ws/`
- **Operations**: Order creation, cancellation, and market data retrieval.

Official documentation is available at [Polymarket Documentation](https://docs.polymarket.com/).

---

## Setting Up the Client
To interact with the CLOB API, you'll need a Polygon wallet and the Python client. Here's how to set it up:

### Prerequisites
- **Polygon Wallet**: Polymarket operates on the Polygon network (chain ID 137). You'll need a private key from:
  - An Externally Owned Account (EOA), or
  - A browser wallet (e.g., Metamask) or email/magic login account.
- **USDC**: The stablecoin used for transactions.

### Installation
Install the Python client via pip:
```bash
pip install py-clob-client
```

### Initialization
Initialize the client with your private key. The setup depends on your wallet type:

#### For an EOA
```python
from py_clob_client.client import ClobClient

host = "https://clob.polymarket.com"
private_key = "your_private_key_here"  # Replace with your Polygon private key
chain_id = 137  # Polygon network

client = ClobClient(host, key=private_key, chain_id=chain_id)
```

#### For Browser Wallet (e.g., Metamask)
Add `signature_type=2` and the Polymarket proxy address:
```python
client = ClobClient(
    host="https://clob.polymarket.com",
    key="your_private_key_here",
    chain_id=137,
    signature_type=2,
    funder="POLYMARKET_PROXY_ADDRESS"  # Provided by Polymarket
)
```

#### For Email/Magic Login
Use `signature_type=1`:
```python
client = ClobClient(
    host="https://clob.polymarket.com",
    key="your_private_key_here",
    chain_id=137,
    signature_type=1,
    funder="POLYMARKET_PROXY_ADDRESS"
)
```

This connects your client to Polymarket's CLOB, ready for authenticated interactions. For more details, see the [Python Client GitHub](https://github.com/Polymarket/py-clob-client).

---

## Authentication Methods
The CLOB API uses two authentication levels:
1. **L1: Private Key Authentication**
   - Required for placing orders and creating API keys.
   - Uses EIP712 signatures with headers:
     - `POLY_ADDRESS`: Your wallet address.
     - `POLY_SIGNATURE`: Signed message.
     - `POLY_TIMESTAMP`: Current timestamp.
     - `POLY_NONCE`: Unique nonce.
   - Signing domain: `{name: "ClobAuthDomain", version: "1", chainId: 137}`.

2. **L2: API Key Authentication**
   - Used for order management and data retrieval.
   - Requires generating an API key:
     ```python
     api_key_data = client.create_api_key()
     print("API Key:", api_key_data.api_key)
     print("Secret:", api_key_data.secret)
     print("Passphrase:", api_key_data.passphrase)
     ```
   - Store these credentials securely (e.g., in an `.env` file).
   - Headers include `POLY_API_KEY`, `POLY_PASSPHRASE`, `POLY_SIGNATURE`, and `POLY_TIMESTAMP`.

Refer to [Polymarket Documentation](https://docs.polymarket.com/#authentication) for examples.

---

## Placing and Managing Orders
Orders represent bets on event outcomes, identified by token IDs. Here's how to handle them:

### Finding Markets and Token IDs
List available markets to find token IDs:
```python
markets = client.get_markets()
for market in markets:
    print(market)  # Displays market details including token_id
```

### Placing an Order
Create and post a limit order (e.g., buy 100 shares at $0.50):
```python
order = client.create_order(
    token_id="some_token_id",  # Replace with actual token ID
    price=0.5,  # Price per share (0 to 1)
    side="buy",  # "buy" or "sell"
    size=100,  # Number of shares
    fee_rate_bps=0  # Fee in basis points (0 for no fee)
)
response = client.post_order(order)
print(response)  # Order confirmation
```

Order types include:
- **FOK (Fill-Or-Kill)**: Executes immediately or cancels.
- **GTC (Good-Til-Cancelled)**: Stays open until filled or canceled.
- **GTD (Good-Til-Day)**: Expires at day's end with a 1-minute buffer.

### Canceling an Order
Cancel an order by its ID:
```python
order_id = "some_order_id"  # From post_order response
client.cancel_order(order_id)
```

Cancel all orders:
```python
client.cancel_all_orders()
```

### Checking Order Status
Retrieve order details:
```python
order = client.get_order(order_id="some_order_id")
print(order)  # Displays status, fill amount, etc.
```

Ensure sufficient USDC balance and allowance for trades. The maximum order size is:
\[ maxOrderSize = underlyingAssetBalance - \sum(orderSize - orderFillAmount) \]

---

## Accessing Market Data
Market data informs trading decisions. Use these methods:

### Get Current Price
```python
price = client.get_price(token_id="some_token_id")
print(price)  # Current price in USDC
```

### View Order Book
```python
book = client.get_book(token_id="some_token_id")
print(book)  # Bids and asks
```

### Real-Time Data via Websocket
Subscribe to the Websocket API for live updates:
- **User Channel**: Tracks your orders/trades (authenticated).
- **Market Channel**: Provides level 2 price data (public).
See [Polymarket Documentation](https://docs.polymarket.com/#websocket-api) for setup.

---

## Fees
Polymarket charges symmetric fees for makers and takers, currently:
- **Maker Fee**: 0 bps (>0 USDC volume).
- **Taker Fee**: 0 bps (>0 USDC volume).

Fee formulas:
- **Selling**: \( feeQuote = baseRate \times \min(price, 1-price) \times size \)
- **Buying**: \( feeBase = baseRate \times \min(price, 1-price) \times \frac{size}{price} \)

Fees are applied to proceeds and displayed transparently. Check [Polymarket Documentation](https://docs.polymarket.com/#fees) for updates.

---

## Security and Compliance
- **Smart Contract**: Audited by Chainsecurity; deployed at `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` on Polygon. See [Audit Report](https://github.com/Polymarket/ctf-exchange/blob/main/audit/ChainSecurity_Polymarket_Exchange_audit.pdf).
- **Non-Custodial**: Users control funds via their wallets.
- **System Status**: Monitor at [https://status-clob.polymarket.com/](https://status-clob.polymarket.com/).
- **Regulatory Note**: US customers are blocked since a 2022 CFTC settlement.

---

## Summary
To interact with Polymarket via the CLOB API:
1. Install `py-clob-client` and initialize it with your Polygon private key.
2. Authenticate using L1 (private key) or L2 (API key) methods.
3. Place and manage orders (buy/sell shares) using token IDs.
4. Access market data via REST or Websocket endpoints.

This setup enables automated trading and data analysis on Polymarket's prediction markets, leveraging its decentralized infrastructure for secure, transparent speculation on real-world events.

# Polymarket Analysis Agent Implementation Guide

This document provides implementation details for the Polymarket Analysis Agent, focusing on system architecture, API interaction, and agent prompt design.

## System Architecture

The Polymarket Analysis Agent consists of three main components:

1. **FastAPI Server**: Provides the HTTP endpoints for user interaction
2. **Polymarket Data Retrieval**: Handles fetching and processing market data
3. **OpenAI Agent**: Processes user queries and provides market analysis

### FastAPI Server

The server exposes a single endpoint `/chat` that accepts POST requests with a JSON body containing the user's input. The response is a server-sent event (SSE) stream that provides real-time updates as the agent processes the query.

```python
@app.post("/chat")
async def chat_stream(request: ChatRequest):
    async def stream():
        try:
            result = Runner.run_streamed(agent, request.input)
            async for event in result.stream_events():
                content = getattr(event, 'data', str(event))
                yield f"data: {content}\n\n"
        except Exception as e:
            yield f"data: Error encountered: {str(e)}\n\n"
    return StreamingResponse(stream(), media_type="text/event-stream")
```

### Polymarket Data Retrieval

We've implemented comprehensive market data retrieval from the Polymarket CLOB API, with several key features:

#### Pagination Handling

The `fetch_all_markets` function handles pagination to retrieve all markets, even when there are thousands of them:

```python
def fetch_all_markets(client: ClobClient, active_only: bool = True, open_only: bool = True) -> List[Dict[str, Any]]:
    all_markets = []
    next_cursor = ""
    
    while True:
        # Get a page of markets
        result = client.get_markets(next_cursor=next_cursor)
        
        # Extract markets and add to collection
        markets = result.get('data', [])
        if not markets:
            break
            
        all_markets.extend(markets)
        
        # Check if there are more pages
        next_cursor = result.get('next_cursor', "")
        if next_cursor == "" or next_cursor == "LTE=":  # Empty or "LTE=" means end of pagination
            break
            
        # Add a small delay to avoid hitting rate limits
        time.sleep(0.1)
    
    # Apply filters if requested
    filtered_markets = [
        market for market in all_markets 
        if (not active_only or market.get('active', False) is True) and 
           (not open_only or market.get('closed', True) is False)
    ]
    
    return filtered_markets
```

#### Market Summary Generation

The `generate_market_summary` function provides a comprehensive overview of markets by category:

```python
def generate_market_summary(markets: List[Dict[str, Any]]) -> str:
    # Convert to DataFrame for analysis
    df = pd.DataFrame(markets)
    
    summary = ["=== Market Summary ==="]
    summary.append(f"Total markets: {len(markets)}")
    
    # Get category breakdown
    category_field = next((field for field in ['category', 'Category'] if field in df.columns), None)
    if category_field:
        category_counts = df[category_field].fillna('Uncategorized').value_counts()
        summary.append("\nTop Categories:")
        for category, count in category_counts.head(10).items():
            summary.append(f"  {category}: {count} markets ({count/len(df)*100:.1f}%)")
    
    # Add upcoming markets by date
    date_field = next((field for field in ['game_start_time', 'end_date_iso', 'end_date'] if field in df.columns), None)
    if date_field:
        # Add upcoming markets sorted by date...
    
    return "\n".join(summary)
```

#### Market Finding by Recency

The `find_most_recent_market` function identifies the most recent market based on start time:

```python
def find_most_recent_market(markets: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Convert to DataFrame for easier filtering
    df = pd.DataFrame(markets)
    
    # Find a date field we can use
    date_field = next((field for field in ['game_start_time', 'end_date_iso', 'end_date'] if field in df.columns), None)
    
    if date_field:
        # Convert to datetime with UTC timezone
        df[date_field] = pd.to_datetime(df[date_field], errors='coerce', utc=True)
        df = df.dropna(subset=[date_field])
        
        if not df.empty:
            # Find closest to now
            now = pd.Timestamp.now(tz='UTC')
            df['time_diff'] = abs(df[date_field] - now)
            return df.sort_values('time_diff').iloc[0].to_dict()
    
    # Fallback
    return markets[0]
```

### Agent Tools

The agent is equipped with several function tools that provide its capabilities:

1. **get_active_open_markets**: Retrieves markets with optional keyword filtering
2. **get_market_details**: Provides detailed information about a specific market
3. **get_most_recent_market**: Finds the most recent market on the platform
4. **get_market_summary**: Generates an overview of all active markets by category
5. **place_limit_order**: Executes trades when authorized

Each tool is implemented as a Python function and decorated with `@function_tool` to make it available to the agent.

## Agent Prompt Design

The agent prompt is critical for providing the right context and instructions. Our prompt has several key sections:

```
prompt = """
You are a Polymarket Expert Analyst - a specialized AI designed to help users navigate and understand prediction markets on Polymarket.com. Polymarket is a decentralized prediction market platform where users can trade on the outcome of events and earn profits if their predictions are correct.

As a Polymarket expert, you understand that prediction markets aggregate information and provide real-time probability estimates of future events. The prices on Polymarket represent the market's estimate of the likelihood of events occurring - for example, a "Yes" share priced at $0.75 means the market collectively estimates a 75% probability of that outcome.

You have access to these powerful tools:

1. **get_active_open_markets**: Retrieves all active and open markets, optionally filtered by keywords. Use this to find markets matching user interests (e.g., ["election", "bitcoin", "NFL"]).

2. **get_market_details**: Provides comprehensive details about a specific market using its condition ID. This includes current prices, trading volume, liquidity, and outcome information.

3. **get_most_recent_market**: Finds the newest market on the platform (based on start time), ideal for discovering trending topics.

4. **get_market_summary**: Generates an overview of all active markets, including category breakdown and upcoming events.

5. **place_limit_order**: Allows placement of limit orders on specific markets (when authorized).

Your analytical approach:

1. EXPLORE: Begin by helping users discover relevant markets using get_active_open_markets with appropriate keywords or get_market_summary for a broader overview.

2. ANALYZE: Once a market is identified, use get_market_details to obtain comprehensive information about prices, volume, and market structure.

3. RESEARCH: Leverage web search to gather the latest news, expert opinions, and data related to the market's subject matter.

4. CONTEXTUALIZE: Provide users with a clear explanation of:
   - What the market is predicting and how to interpret the prices
   - Current market sentiment and what it implies
   - How recent events might impact the market outcome
   - Important factors and developments to monitor

5. ASSESS: Offer your evaluation of whether the current market prices seem justified based on available information.

6. EDUCATE: Help users understand how prediction markets work, explaining concepts like market efficiency, price discovery, and how to interpret probability estimates.

When responding to users, be conversational yet precise. Avoid financial advice but help users understand the data and probabilities the markets are reflecting. Guide users through the process of exploring markets, understanding the odds, and interpreting what the collective wisdom of traders is saying about future events.
"""
```

### Key Elements of the Prompt

1. **Identity and Purpose**: Establishes the agent as a Polymarket Expert Analyst with a clear purpose
2. **Conceptual Framework**: Explains prediction markets and probability interpretation
3. **Tool Description**: Outlines each tool with its purpose and usage patterns
4. **Analytical Approach**: Provides a structured methodology (EXPLORE, ANALYZE, RESEARCH, etc.)
5. **Communication Style**: Directs the agent to be conversational yet precise, avoiding financial advice
6. **Educational Role**: Emphasizes helping users understand market concepts

## Error Handling

The system includes robust error handling at multiple levels:

1. **API Response Validation**: Checks for expected data structures
2. **Exception Handling**: Captures and formats exceptions for user-friendly display
3. **Fallback Mechanisms**: Provides alternative approaches when primary methods fail
4. **Data Cleansing**: Handles missing or malformed data gracefully

## Extending the Agent

To extend the agent with new capabilities:

1. **Add New Functions**: Implement new functionality as Python functions
2. **Decorate as Tools**: Use `@function_tool` to make them available to the agent
3. **Update Prompt**: Document new tools in the agent prompt
4. **Register Tools**: Add new tools to the agent initialization

Example of adding a new tool:

```python
@function_tool
def analyze_market_trend(condition_id: str) -> str:
    """
    Analyze the price trend of a market over time.
    
    Args:
        condition_id: The condition ID of the market to analyze
        
    Returns:
        Formatted trend analysis
    """
    # Implementation...
    return analysis

# Update agent initialization
agent = Agent(
    name="PolymarketAnalyst", 
    instructions=prompt, 
    tools=[
        WebSearchTool(), 
        get_active_open_markets, 
        get_market_details, 
        get_most_recent_market, 
        get_market_summary, 
        place_limit_order,
        analyze_market_trend  # New tool
    ]
)
```

## Security and Authentication

The agent supports two methods of authentication with the Polymarket API:

1. **Private Key Authentication**: Using a wallet private key
2. **API Key Authentication**: Using API credentials (key, secret, passphrase)

Configuration is done via environment variables in the `.env` file, with appropriate validation to ensure at least one method is configured.

## Performance Considerations

For optimal performance:

1. **Use Pagination**: The `fetch_all_markets` function handles pagination efficiently
2. **Add Rate Limiting**: Small delays between requests prevent API rate limiting
3. **Filter Early**: Apply filters as soon as possible to reduce data processing
4. **Use DataFrame Operations**: Pandas enables efficient data manipulation
5. **Cache Common Data**: Consider caching market data for frequent operations

## Testing

Test the agent with a variety of queries:

```bash
# Get a market summary
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"input": "Summarize the current markets"}' --no-buffer

# Find markets by keyword
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"input": "Find NFL markets"}' --no-buffer

# Analyze a specific market
curl -X POST "http://localhost:8000/chat" -H "Content-Type: application/json" -d '{"input": "Analyze the market with condition ID XYZ"}' --no-buffer
```