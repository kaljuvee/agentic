import csv
import json
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

# Generate or derive API credentials
api_creds = client.create_or_derive_api_creds()
client.set_api_creds(api_creds)

# Initialize variables for pagination
markets_list = []
next_cursor = None
total_records = 0

# Fetch all available markets using pagination
while True:
    try:
        print(f"Fetching markets with next_cursor: {next_cursor}")
        # Make the API call based on the cursor value
        response = client.get_markets(next_cursor=next_cursor) if next_cursor else client.get_markets()
        
        # Check if the response contains data
        if 'data' not in response:
            print("No data found in response.")
            break

        batch_size = len(response['data'])
        total_records += batch_size
        print(f"Fetched {batch_size} records in this batch. Total records so far: {total_records}")
        
        markets_list.extend(response['data'])
        next_cursor = response.get("next_cursor")

        # Exit loop if there's no next_cursor
        if not next_cursor:
            break
    except Exception as e:
        print(f"Exception occurred: {e}")
        break

print(f"\nFinal total number of records fetched: {total_records}")

# Debugging: Print raw market data
print("Raw Market Data:")
print(json.dumps(markets_list, indent=2))

# Dynamically extract all keys for CSV columns
csv_columns = set()
for market in markets_list:
    csv_columns.update(market.keys())
    if 'tokens' in market:
        csv_columns.update({f"token_{key}" for token in market['tokens'] for key in token.keys()})
csv_columns = sorted(csv_columns)  # Sort columns alphabetically

# Write to CSV
csv_file = "data/markets_data.csv"
try:
    with open(csv_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for market in markets_list:
            row = {}
            for key in csv_columns:
                if key.startswith("token_"):
                    token_key = key[len("token_"):]
                    row[key] = ', '.join([str(token.get(token_key, 'N/A')) for token in market.get('tokens', [])])
                else:
                    row[key] = market.get(key, 'N/A')
            writer.writerow(row)
    print(f"Data has been written to {csv_file} successfully.")
except IOError as e:
    print(f"Error writing to CSV: {e}")