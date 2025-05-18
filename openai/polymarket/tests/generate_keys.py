from py_clob_client.client import ClobClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Replace with your private key from Polymarket
private_key = os.getenv("POLYMARKET_PRIVATE_KEY")
host = "https://clob.polymarket.com"
chain_id = 137  # Polygon Mainnet

# Initialize the client
client = ClobClient(host, key=private_key, chain_id=chain_id)

try:
    # Generate or derive API credentials
    api_creds = client.create_or_derive_api_creds()
    
    # Print the credentials
    print("API Credentials Generated Successfully:")
    print(f"POLYMARKET_API_KEY={api_creds.api_key}")
    print(f"POLYMARKET_API_SECRET={api_creds.secret}")
    print(f"POLYMARKET_API_PASSPHRASE={api_creds.passphrase}")

except Exception as e:
    print(f"Error generating API credentials: {e}")