import requests
import json

markets = requests.get("https://gamma-api.polymarket.com/markets")
print(markets.json())

with open("data/markets.json", "w") as f:
    json.dump(markets.json(), f)