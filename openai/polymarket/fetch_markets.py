#!/usr/bin/env python3

import os
from dotenv import load_dotenv
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import ApiCreds
import pandas as pd
from typing import Dict, Any, List
import time

# Load environment variables
load_dotenv()

def initialize_clob_client():
    """Initialize the CLOB client with API credentials from environment variables"""
    host = os.getenv("POLYMARKET_HOST", "https://clob.polymarket.com")
    chain_id = int(os.getenv("CHAIN_ID", "137"))
    
    # Use API credentials for authentication
    api_key = os.getenv("POLYMARKET_API_KEY")
    api_secret = os.getenv("POLYMARKET_API_SECRET")
    api_passphrase = os.getenv("POLYMARKET_API_PASSPHRASE")
    
    if not (api_key and api_secret and api_passphrase):
        raise ValueError("API credentials (POLYMARKET_API_KEY, POLYMARKET_API_SECRET, POLYMARKET_API_PASSPHRASE) are required")
    
    # Create API credentials object
    creds = ApiCreds(
        api_key=api_key,
        api_secret=api_secret,
        api_passphrase=api_passphrase
    )
    
    # Initialize the CLOB client
    client = ClobClient(host, chain_id=chain_id, creds=creds)
    
    return client

def fetch_all_markets(client: ClobClient) -> List[Dict[str, Any]]:
    """
    Fetch all markets from the CLOB API with pagination
    
    Args:
        client: Initialized CLOB client
        
    Returns:
        List of all markets
    """
    all_markets = []
    next_cursor = ""
    
    print("Fetching markets from CLOB API...")
    
    while True:
        # Get a page of markets
        result = client.get_markets(next_cursor=next_cursor)
        
        if not result or not isinstance(result, dict):
            print(f"Unexpected response format: {result}")
            break
        
        # Extract markets from the response
        markets = result.get('data', [])
        if not markets:
            break
            
        # Add to our collection
        all_markets.extend(markets)
        print(f"Fetched {len(markets)} markets, total so far: {len(all_markets)}")
        
        # Check if there are more pages
        next_cursor = result.get('next_cursor', "")
        if next_cursor == "" or next_cursor == "LTE=":  # Empty or "LTE=" means end of pagination
            break
            
        # Add a small delay to avoid hitting rate limits
        time.sleep(0.1)
    
    print(f"Total markets fetched: {len(all_markets)}")
    
    # Filter for active and open markets only
    active_open_markets = [
        market for market in all_markets 
        if market.get('active', False) is True and market.get('closed', True) is False
    ]
    
    print(f"Active and open markets: {len(active_open_markets)} out of {len(all_markets)}")
    
    return active_open_markets

def generate_market_summary(markets: List[Dict[str, Any]]) -> str:
    """
    Generate a summary of markets by category
    
    Args:
        markets: List of markets
        
    Returns:
        Formatted string with summary information
    """
    if not markets:
        return "No markets available for summary"
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(markets)
    
    summary = ["=== Market Summary ==="]
    summary.append(f"Total active and open markets: {len(markets)}")
    
    # Print the available columns for debugging
    summary.append(f"\nAvailable fields in market data: {', '.join(df.columns.tolist())}")
    
    # Get category breakdown if available
    category_field = None
    for possible_field in ['category', 'Category']:
        if possible_field in df.columns:
            category_field = possible_field
            break
    
    if category_field:
        category_counts = df[category_field].fillna('Uncategorized').value_counts()
        
        summary.append("\nTop Categories:")
        for category, count in category_counts.head(10).items():
            summary.append(f"  {category}: {count} markets ({count/len(df)*100:.1f}%)")
    
    # Get upcoming markets (closest game start time)
    game_start_field = None
    for possible_field in ['game_start_time', 'end_date_iso', 'end_date']:
        if possible_field in df.columns:
            game_start_field = possible_field
            break
    
    if game_start_field:
        try:
            # Convert to datetime, handling both string formats and None values
            df[game_start_field] = pd.to_datetime(df[game_start_field], errors='coerce', utc=True)
            df = df.dropna(subset=[game_start_field])
            
            if not df.empty:
                upcoming_markets = df.sort_values(game_start_field).head(5)
                
                summary.append(f"\nUpcoming Markets (by {game_start_field}):")
                for i, (_, market) in enumerate(upcoming_markets.iterrows()):
                    question_field = 'question' if 'question' in market else 'Question' if 'Question' in market else None
                    question = market.get(question_field, 'N/A') if question_field else 'N/A'
                    game_start = market[game_start_field]
                    category = market.get(category_field, 'Uncategorized') if category_field else 'Uncategorized'
                    summary.append(f"  {i+1}. {question} (Category: {category}, Date: {game_start})")
        except Exception as e:
            summary.append(f"\nError processing dates: {str(e)}")
    
    # Add sample of market data for debugging
    if len(markets) > 0:
        sample_market = markets[0]
        summary.append("\nSample Market Data (First Market):")
        for key, value in sample_market.items():
            if isinstance(value, dict) or isinstance(value, list):
                summary.append(f"  {key}: {type(value).__name__}")
            else:
                summary.append(f"  {key}: {value}")
    
    return "\n".join(summary)

def find_most_recent_market(markets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Find the most recent market based on game start time
    
    Args:
        markets: List of markets
        
    Returns:
        The most recent market
    """
    if not markets:
        return None
    
    # Try to sort by game_start_time or end_date_iso if available
    try:
        # Convert markets to DataFrame for easier filtering
        df = pd.DataFrame(markets)
        
        # Find a date field we can use
        date_field = None
        for possible_field in ['game_start_time', 'end_date_iso', 'end_date']:
            if possible_field in df.columns:
                date_field = possible_field
                break
        
        if date_field:
            # Convert to datetime with UTC timezone
            df[date_field] = pd.to_datetime(df[date_field], errors='coerce', utc=True)
            df = df.dropna(subset=[date_field])
            
            if not df.empty:
                # Sort by date field in ascending order (closest to now)
                now = pd.Timestamp.now(tz='UTC')
                df['time_diff'] = abs(df[date_field] - now)
                sorted_df = df.sort_values('time_diff')
                return sorted_df.iloc[0].to_dict()
    except Exception as e:
        print(f"Error sorting markets: {e}")
    
    # If we can't sort or there's an error, return the first market
    return markets[0]

def get_market_metadata(client: ClobClient, condition_id: str) -> Dict[str, Any]:
    """
    Get detailed metadata for a specific market
    
    Args:
        client: Initialized CLOB client
        condition_id: Condition ID of the market
        
    Returns:
        Market metadata
    """
    try:
        market = client.get_market(condition_id=condition_id)
        return market
    except Exception as e:
        print(f"Error getting market metadata: {e}")
        return None

def format_market_info(market: Dict[str, Any]) -> str:
    """
    Format market information for display
    
    Args:
        market: Market data
        
    Returns:
        Formatted string with market information
    """
    if not market:
        return "No market data available"
    
    # Basic information
    formatted = [
        "=== Market Information ===",
        f"Question: {market.get('question', 'N/A')}",
        f"Description: {market.get('description', 'N/A')[:150]}..." if len(market.get('description', '')) > 150 else f"Description: {market.get('description', 'N/A')}",
        f"Condition ID: {market.get('condition_id', 'N/A')}",
        f"Category: {market.get('category', 'N/A')}",
        f"Market Slug: {market.get('market_slug', 'N/A')}",
        f"End Date: {market.get('end_date_iso', 'N/A')}",
        f"Game Start Time: {market.get('game_start_time', 'N/A')}",
        f"Active: {market.get('active', 'N/A')}",
        f"Closed: {market.get('closed', 'N/A')}",
        f"FPMM Address: {market.get('fpmm', 'N/A')}",
        f"Minimum Order Size: {market.get('minimum_order_size', 'N/A')}",
        f"Minimum Tick Size: {market.get('minimum_tick_size', 'N/A')}",
    ]
    
    # Tokens/outcomes information
    if 'tokens' in market and isinstance(market['tokens'], list):
        formatted.append("\n=== Outcomes ===")
        for token in market['tokens']:
            if isinstance(token, dict):
                outcome = token.get('outcome', 'Unknown')
                token_id = token.get('token_id', 'N/A')
                formatted.append(f"- {outcome}: Token ID={token_id}")
    
    # Rewards information
    if 'rewards' in market and isinstance(market['rewards'], dict):
        formatted.append("\n=== Rewards Configuration ===")
        rewards = market['rewards']
        formatted.append(f"Min Size: {rewards.get('min_size', 'N/A')}")
        formatted.append(f"Max Spread: {rewards.get('max_spread', 'N/A')}")
        formatted.append(f"Event Start Date: {rewards.get('event_start_date', 'N/A')}")
        formatted.append(f"Event End Date: {rewards.get('event_end_date', 'N/A')}")
        formatted.append(f"In-Game Multiplier: {rewards.get('in_game_multiplier', 'N/A')}")
        formatted.append(f"Reward Epoch: {rewards.get('reward_epoch', 'N/A')}")
    
    return "\n".join(formatted)

def main():
    try:
        # Initialize CLOB client
        client = initialize_clob_client()
        
        # Fetch all markets
        markets = fetch_all_markets(client)
        
        # Check if we found any markets
        if not markets:
            print("No markets found")
            return
            
        # Generate and print market summary
        market_summary = generate_market_summary(markets)
        print(f"\n{market_summary}")
        
        # Find the most recent market
        most_recent_market = find_most_recent_market(markets)
        
        if not most_recent_market:
            print("Could not determine the most recent market")
            return
            
        print(f"\nMost recent market question: {most_recent_market.get('question', most_recent_market.get('Question', 'N/A'))}")
        
        # Get detailed metadata for the most recent market
        condition_id = most_recent_market.get('condition_id', most_recent_market.get('conditionId', None))
        if not condition_id:
            print("The most recent market does not have a condition ID")
            print("Available fields in most recent market:", ', '.join(most_recent_market.keys()))
            return
            
        print(f"Fetching detailed metadata for condition ID: {condition_id}")
        market_metadata = get_market_metadata(client, condition_id)
        
        # Format and print the market information
        formatted_info = format_market_info(market_metadata)
        print("\n" + formatted_info)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 