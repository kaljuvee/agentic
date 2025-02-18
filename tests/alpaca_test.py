import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

def test_alpaca_orders():
    """
    Test placing market and limit orders for MSFT using Alpaca API
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize the trading client
    api_key = os.getenv('ALPACA_PAPER_API_KEY')
    secret_key = os.getenv('ALPACA_PAPER_SECRET_KEY')
    
    # Debug: Check if credentials are loaded
    if not api_key or not secret_key:
        print("❌ Error: API credentials not found in environment variables")
        print("Make sure you have ALPACA_PAPER_API_KEY and ALPACA_PAPER_SECRET_KEY in your .env file")
        return
        
    print(f"API Key found: {api_key[:5]}...")  # Only print first 5 chars for security
    
    trading_client = TradingClient(api_key, secret_key, paper=True)

    print("\nTesting Alpaca Paper Trading Orders")
    print("=" * 50)
    print("Using paper trading environment")

    try:
        # Test Market Order
        print("\nTesting Market Order:")
        market_order_data = MarketOrderRequest(
            symbol="MSFT",
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )

        market_order = trading_client.submit_order(
            order_data=market_order_data
        )
        
        print(f"✅ Market order placed successfully:")
        print(f"   Symbol: {market_order.symbol}")
        print(f"   Quantity: {market_order.qty}")
        print(f"   Side: {market_order.side}")
        print(f"   Status: {market_order.status}")

        # Test Limit Order
        print("\nTesting Limit Order:")
        # Set a fixed limit price for testing (e.g., $300 for MSFT)
        limit_price = 300.00

        limit_order_data = LimitOrderRequest(
            symbol="MSFT",
            qty=1,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY,
            limit_price=limit_price
        )

        limit_order = trading_client.submit_order(
            order_data=limit_order_data
        )

        print(f"✅ Limit order placed successfully:")
        print(f"   Symbol: {limit_order.symbol}")
        print(f"   Quantity: {limit_order.qty}")
        print(f"   Side: {limit_order.side}")
        print(f"   Limit Price: {limit_order.limit_price}")
        print(f"   Status: {limit_order.status}")

    except Exception as e:
        print(f"❌ Error during test: {str(e)}")

if __name__ == "__main__":
    test_alpaca_orders()
