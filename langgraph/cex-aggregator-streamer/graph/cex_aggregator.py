from typing import Literal, Optional, TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
import ccxt
from graph.exchange_factory import exchanges, exchange_base_currencies, pairs_black_list

#https://github.com/langchain-ai/langgraph/blob/main/docs/docs/concepts/low_level.md
# Load environment variables
load_dotenv()

# Define the state type
class CexState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: Optional[str]

@tool
def get_exchange_list() -> str:
    """Get a list of all available exchanges."""
    try:
        exchange_list = list(exchanges.keys())
        return f"Available exchanges: {', '.join(exchange_list)}"
    except Exception as e:
        return f"Error getting exchange list: {str(e)}"

@tool
def get_balance(exchange_name: str) -> str:
    """
    Get account balance for a specific exchange.
    
    Parameters:
        exchange_name: The name of the exchange (e.g., 'binance', 'bybit')
    """
    try:
        exchange_name = exchange_name.lower()
        if exchange_name not in exchanges:
            return f"Exchange '{exchange_name}' not found. Available exchanges: {', '.join(exchanges.keys())}"
        
        exchange = exchanges[exchange_name]
        
        # Fetch balance
        balance = exchange.fetch_balance()
        
        # Format the response
        response = f"Balance on {exchange_name.capitalize()}:\n"
        
        # Add total balances
        if 'total' in balance:
            total_balances = {k: v for k, v in balance['total'].items() if v > 0}
            if total_balances:
                response += "\nTotal Balances:\n"
                for currency, amount in total_balances.items():
                    response += f"- {currency}: {amount}\n"
            else:
                response += "\nNo assets found.\n"
        
        # Add free balances
        if 'free' in balance:
            free_balances = {k: v for k, v in balance['free'].items() if v > 0}
            if free_balances:
                response += "\nAvailable Balances:\n"
                for currency, amount in free_balances.items():
                    response += f"- {currency}: {amount}\n"
        
        # Add used balances
        if 'used' in balance:
            used_balances = {k: v for k, v in balance['used'].items() if v > 0}
            if used_balances:
                response += "\nIn Use (Orders/Positions):\n"
                for currency, amount in used_balances.items():
                    response += f"- {currency}: {amount}\n"
        
        return response
    except ccxt.AuthenticationError:
        return f"Authentication error for {exchange_name}. Please check your API keys."
    except ccxt.NetworkError:
        return f"Network error when connecting to {exchange_name}. Please try again later."
    except Exception as e:
        return f"Error getting balance for {exchange_name}: {str(e)}"

@tool
def get_ticker(exchange_name: str, symbol: str) -> str:
    """
    Get current ticker information for a specific symbol on an exchange.
    
    Parameters:
        exchange_name: The name of the exchange (e.g., 'binance', 'bybit')
        symbol: The trading pair symbol (e.g., 'BTC/USDT')
    """
    try:
        exchange_name = exchange_name.lower()
        if exchange_name not in exchanges:
            return f"Exchange '{exchange_name}' not found. Available exchanges: {', '.join(exchanges.keys())}"
        
        exchange = exchanges[exchange_name]
        
        # Format symbol if needed
        if '/' not in symbol:
            # Try to guess the format based on common patterns
            if exchange_name in exchange_base_currencies:
                base_currency = exchange_base_currencies[exchange_name]
                symbol = f"{symbol}/{base_currency}"
        
        # Fetch ticker
        ticker = exchange.fetch_ticker(symbol)
        
        # Format the response
        response = f"Ticker for {symbol} on {exchange_name.capitalize()}:\n"
        response += f"- Last Price: {ticker['last']}\n"
        response += f"- Bid: {ticker['bid']}\n"
        response += f"- Ask: {ticker['ask']}\n"
        response += f"- 24h High: {ticker['high']}\n"
        response += f"- 24h Low: {ticker['low']}\n"
        response += f"- 24h Volume: {ticker['baseVolume']}\n"
        response += f"- 24h Change: {ticker.get('percentage', 'N/A')}%\n"
        response += f"- Last Updated: {ticker['datetime']}\n"
        
        return response
    except ccxt.BadSymbol:
        return f"Invalid symbol '{symbol}' for {exchange_name}. Please check the symbol format."
    except ccxt.NetworkError:
        return f"Network error when connecting to {exchange_name}. Please try again later."
    except Exception as e:
        return f"Error getting ticker for {symbol} on {exchange_name}: {str(e)}"

@tool
def get_markets(exchange_name: str, limit: int = 10) -> str:
    """
    Get available markets/trading pairs for a specific exchange.
    
    Parameters:
        exchange_name: The name of the exchange (e.g., 'binance', 'bybit')
        limit: Maximum number of markets to return (default: 10)
    """
    try:
        exchange_name = exchange_name.lower()
        if exchange_name not in exchanges:
            return f"Exchange '{exchange_name}' not found. Available exchanges: {', '.join(exchanges.keys())}"
        
        exchange = exchanges[exchange_name]
        
        # Fetch markets
        markets = exchange.fetch_markets()
        
        # Format the response
        response = f"Available Markets on {exchange_name.capitalize()}:\n"
        
        # Get blacklisted pairs for this exchange
        blacklist = pairs_black_list.get(exchange_name, [])
        
        # Filter out blacklisted pairs and limit the number of results
        filtered_markets = [m for m in markets if m['symbol'] not in blacklist][:limit]
        
        for market in filtered_markets:
            response += f"\n- {market['symbol']}"
            if 'active' in market:
                response += f" (Active: {market['active']})"
        
        response += f"\n\nShowing {len(filtered_markets)} of {len(markets)} markets."
        
        return response
    except ccxt.NetworkError:
        return f"Network error when connecting to {exchange_name}. Please try again later."
    except Exception as e:
        return f"Error getting markets for {exchange_name}: {str(e)}"

@tool
def get_order_book(exchange_name: str, symbol: str, limit: int = 5) -> str:
    """
    Get the current order book for a specific symbol on an exchange.
    
    Parameters:
        exchange_name: The name of the exchange (e.g., 'binance', 'bybit')
        symbol: The trading pair symbol (e.g., 'BTC/USDT')
        limit: Number of orders to show on each side (default: 5)
    """
    try:
        exchange_name = exchange_name.lower()
        if exchange_name not in exchanges:
            return f"Exchange '{exchange_name}' not found. Available exchanges: {', '.join(exchanges.keys())}"
        
        exchange = exchanges[exchange_name]
        
        # Format symbol if needed
        if '/' not in symbol:
            # Try to guess the format based on common patterns
            if exchange_name in exchange_base_currencies:
                base_currency = exchange_base_currencies[exchange_name]
                symbol = f"{symbol}/{base_currency}"
        
        # Fetch order book
        order_book = exchange.fetch_order_book(symbol, limit)
        
        # Format the response
        response = f"Order Book for {symbol} on {exchange_name.capitalize()}:\n"
        
        # Add asks (sell orders)
        response += "\nAsks (Sell Orders):\n"
        for price, amount in order_book['asks'][:limit]:
            response += f"- Price: {price}, Amount: {amount}\n"
        
        # Add bids (buy orders)
        response += "\nBids (Buy Orders):\n"
        for price, amount in order_book['bids'][:limit]:
            response += f"- Price: {price}, Amount: {amount}\n"
        
        return response
    except ccxt.BadSymbol:
        return f"Invalid symbol '{symbol}' for {exchange_name}. Please check the symbol format."
    except ccxt.NetworkError:
        return f"Network error when connecting to {exchange_name}. Please try again later."
    except Exception as e:
        return f"Error getting order book for {symbol} on {exchange_name}: {str(e)}"

@tool
def compare_prices(symbol: str, exchange_list: Optional[List[str]] = None) -> str:
    """
    Compare prices for a specific symbol across multiple exchanges.
    
    Parameters:
        symbol: The trading pair symbol (e.g., 'BTC/USDT')
        exchange_list: Optional list of exchanges to compare (if None, uses all available exchanges)
    """
    try:
        if exchange_list is None:
            exchange_list = list(exchanges.keys())
        else:
            # Convert to lowercase and filter valid exchanges
            exchange_list = [e.lower() for e in exchange_list if e.lower() in exchanges]
        
        if not exchange_list:
            return "No valid exchanges specified for comparison."
        
        results = []
        
        # Format symbol if needed for each exchange
        for exchange_name in exchange_list:
            try:
                exchange = exchanges[exchange_name]
                
                # Adjust symbol format if needed
                current_symbol = symbol
                if '/' not in current_symbol and exchange_name in exchange_base_currencies:
                    base_currency = exchange_base_currencies[exchange_name]
                    current_symbol = f"{current_symbol}/{base_currency}"
                
                # Fetch ticker
                ticker = exchange.fetch_ticker(current_symbol)
                
                # Store result
                results.append({
                    'exchange': exchange_name,
                    'symbol': current_symbol,
                    'price': ticker['last'],
                    'bid': ticker['bid'],
                    'ask': ticker['ask'],
                    'spread': ticker['ask'] - ticker['bid'] if ticker['ask'] and ticker['bid'] else None
                })
            except Exception as e:
                # Skip exchanges with errors
                continue
        
        if not results:
            return f"Could not find price information for {symbol} on any of the specified exchanges."
        
        # Sort by price
        results.sort(key=lambda x: x['price'] if x['price'] else float('inf'))
        
        # Format the response
        response = f"Price Comparison for {symbol}:\n"
        
        for result in results:
            response += f"\n{result['exchange'].capitalize()} ({result['symbol']}):\n"
            response += f"- Last Price: {result['price']}\n"
            response += f"- Bid: {result['bid']}\n"
            response += f"- Ask: {result['ask']}\n"
            if result['spread'] is not None:
                response += f"- Spread: {result['spread']}\n"
        
        # Add price difference information
        if len(results) > 1:
            lowest = results[0]
            highest = results[-1]
            if lowest['price'] and highest['price']:
                diff = highest['price'] - lowest['price']
                diff_percent = (diff / lowest['price']) * 100
                response += f"\nPrice Difference: {diff} ({diff_percent:.2f}%)\n"
                response += f"Lowest: {lowest['exchange'].capitalize()} at {lowest['price']}\n"
                response += f"Highest: {highest['exchange'].capitalize()} at {highest['price']}\n"
        
        return response
    except Exception as e:
        return f"Error comparing prices: {str(e)}"

# Initialize tools
tools = [
    get_exchange_list,
    get_balance,
    get_ticker,
    get_markets,
    get_order_book,
    compare_prices
]

# Initialize the model with a specific prompt
system_prompt = """You are a professional cryptocurrency exchange assistant. Your task is to help users 
interact with various cryptocurrency exchanges by providing information about balances, prices, markets, and more.

You have access to the following tools:
1. get_exchange_list: List all available exchanges
2. get_balance: Check account balance on a specific exchange
3. get_ticker: Get current price and information for a trading pair
4. get_markets: View available markets/trading pairs on an exchange
5. get_order_book: View current buy and sell orders for a trading pair
6. compare_prices: Compare prices for a trading pair across multiple exchanges

When helping users:
1. Always confirm which exchange they want to use if not specified
2. Format trading pairs correctly (e.g., BTC/USDT, ETH/USD)
3. Provide clear explanations of market data
4. Handle errors gracefully and suggest alternatives

Remember to:
1. Be precise with numbers and symbols
2. Maintain a professional tone
3. Explain any errors clearly
4. Suggest related information that might be helpful
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

def call_model(state: CexState):
    """Call the model with the current state."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Create and configure the graph
def create_graph():
    """Create and configure the LangGraph for the CEX aggregator agent."""
    # Create the graph
    workflow = StateGraph(CexState)
    
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
    thread_id: str = "cex_demo"
) -> str:
    """
    Stream a response from the CEX aggregator agent for a given question.
    
    Args:
        question (str): The user's cryptocurrency exchange-related question
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
    thread_id: str = "cex_demo"
) -> dict:
    """
    Get a response from the CEX aggregator agent for a given question.
    
    Args:
        question (str): The user's cryptocurrency exchange-related question
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
    question = "What exchanges are available?"
    final_state = get_response(question)
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")