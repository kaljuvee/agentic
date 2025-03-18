from dotenv import load_dotenv
import os
import ccxt
# Load environment variables from .env file
load_dotenv()

# Initialize exchange clients using environment variables
exchanges = {
    'bitstamp': ccxt.bitstamp({
        'apiKey': os.getenv('BITSTAMP_API_KEY'),
        'secret': os.getenv('BITSTAMP_SECRET'),
        'uid': os.getenv('BITSTAMP_UID')
    }),
    'binance': ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET')
    }),
    'kraken': ccxt.kraken({
        'apiKey': os.getenv('KRAKEN_API_KEY'),
        'secret': os.getenv('KRAKEN_SECRET')
    }),
    'poloniex': ccxt.poloniex({
        'apiKey': os.getenv('POLONIEX_API_KEY'),
        'secret': os.getenv('POLONIEX_SECRET')
    }),
    # Bybit
    'bybit': ccxt.bybit({
        'apiKey': os.getenv('BYBIT_API_KEY'),
        'secret': os.getenv('BYBIT_SECRET')
    }),
    # OKX
    'okx': ccxt.okx({
        'apiKey': os.getenv('OKX_API_KEY'),
        'secret': os.getenv('OKX_SECRET'),
        'password': os.getenv('OKX_PASSWORD')
    }),
}

exchange_base_currencies = {'kraken': 'USD', 'binance': 'USDT', 'bitstamp': 'USD', 'poloniex': 'USDT', 'bybit': 'USDT', 'okx': 'USDC'}

pairs_black_list = {'okx': ['USDT/UDSC'], 'binance': ['USDT/UDSC']}