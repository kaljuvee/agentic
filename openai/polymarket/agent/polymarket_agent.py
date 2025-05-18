from agents import Agent, Runner, function_tool
import requests
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

class Config:
    GAMMA_API_HOST = "https://gamma-api.polymarket.com"
    MAX_PROMPT_LENGTH = 500
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Initialize OpenAI client
if not Config.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")
openai.api_key = Config.OPENAI_API_KEY

def _get_active_open_markets(limit: Optional[int] = None, keywords: Optional[List[str]] = None) -> str:
    """
    Gets all active and open markets on Polymarket using Gamma API, optionally filtered by keywords.
    
    Args:
        limit: Maximum number of markets to return
        keywords: Optional list of keywords to filter markets (e.g. ["bitcoin", "election"])
        
    Returns:
        Formatted string with market information
    """
    try:
        # Set default limit if not provided
        if limit is None:
            limit = 100
            
        # Fetch markets from Gamma API
        response = requests.get(
            f"{Config.GAMMA_API_HOST}/markets",
            params={
                "active": "true",
                "closed": "false",
                "archived": "false",
                "limit": limit
            }
        )
        response.raise_for_status()
        markets = response.json()
        
        if not markets:
            return "No active and open markets found"
            
        # Convert to DataFrame for analysis
        df = pd.DataFrame(markets)
        
        # If keywords are provided, filter the markets
        if keywords:
            keyword_results = []
            for keyword in keywords:
                matching_markets = df[df['question'].str.contains(keyword, case=False)]
                if len(matching_markets) > 0:
                    keyword_results.append(f"\n### Markets with '{keyword}' ({len(matching_markets)} markets)")
                    for i, (_, market) in enumerate(matching_markets.head(limit).iterrows()):
                        volume_info = f", Volume: {market.get('volume', 'N/A')}"
                        liquidity_info = f", Liquidity: {market.get('liquidity', 'N/A')}"
                        category_info = f", Category: {market.get('category', 'Uncategorized')}"
                        end_date = f", End Date: {market.get('end_date', 'N/A')}"
                        start_date = f", Start Date: {market.get('start_date', 'N/A')}"
                        keyword_results.append(f"  {i+1}. {market['question']} (Market ID: {market['id']}{volume_info}{liquidity_info}{category_info}{start_date}{end_date})")
                    
                    if len(matching_markets) > limit:
                        keyword_results.append(f"     ... and {len(matching_markets) - limit} more '{keyword}' markets")
            
            if keyword_results:
                return f"Found {len(markets)} active and open markets in total.\nFiltered by keywords: {', '.join(keywords)}\n" + "\n".join(keyword_results)
            else:
                return f"Found {len(markets)} active and open markets, but none match the provided keywords: {', '.join(keywords)}"
        
        # Group by categories if no keywords provided
        category_results = []
        
        # Get unique categories
        categories = df['category'].unique()
        
        # Add summary
        category_results.append(f"Found {len(markets)} active and open markets in total")
        
        # Add category breakdown
        category_counts = df['category'].value_counts()
        category_results.append("\nTop Categories:")
        for category, count in category_counts.head(10).items():
            category_results.append(f"  {category}: {count} markets ({count/len(df)*100:.1f}%)")
        
        # Add markets by category
        category_results.append("\n## Markets by Category (Top markets per category)")
        for category in categories:
            category_markets = df[df['category'] == category]
            
            # Skip if too few markets
            if len(category_markets) == 0:
                continue
                
            # Sort by volume if possible
            if not category_markets['volume'].isnull().all() and not (category_markets['volume'] == 0).all():
                category_markets = category_markets.sort_values('volume', ascending=False)
            
            category_results.append(f"\n### {category} ({len(category_markets)} markets)")
            
            # Display top markets per category
            for i, (_, market) in enumerate(category_markets.head(limit).iterrows()):
                if i >= limit:
                    break
                volume_info = f", Volume: {market.get('volume', 'N/A')}"
                liquidity_info = f", Liquidity: {market.get('liquidity', 'N/A')}"
                end_date = f", End Date: {market.get('end_date', 'N/A')}"
                start_date = f", Start Date: {market.get('start_date', 'N/A')}"
                category_results.append(f"  {i+1}. {market['question']} (Market ID: {market['id']}{volume_info}{liquidity_info}{start_date}{end_date})")
            
            # If there are more markets in this category, mention it
            if len(category_markets) > limit:
                category_results.append(f"     ... and {len(category_markets) - limit} more {category} markets")
        
        return "\n".join(category_results)
        
    except Exception as e:
        return f"Error getting active and open markets: {str(e)}"

@function_tool
def get_active_open_markets(limit: Optional[int] = None, keywords: Optional[List[str]] = None) -> str:
    return _get_active_open_markets(limit=limit, keywords=keywords)

def _get_market_details(market_id: str) -> str:
    """
    Get detailed information about a specific market using Gamma API.
    
    Args:
        market_id: The ID of the market to get details for
        
    Returns:
        Formatted string with detailed market information
    """
    try:
        response = requests.get(f"{Config.GAMMA_API_HOST}/markets/{market_id}")
        response.raise_for_status()
        market = response.json()
        
        # Extract basic information
        question = market.get('question', 'N/A')
        description = market.get('description', 'N/A')
        active = market.get('active', False)
        closed = market.get('closed', False)
        category = market.get('category', 'N/A')
        volume = market.get('volume', 'N/A')
        liquidity = market.get('liquidity', 'N/A')
        start_date = market.get('start_date', 'N/A')
        end_date = market.get('end_date', 'N/A')
        
        # Get outcomes information
        outcomes_info = []
        if 'outcomePrices' in market and isinstance(market['outcomePrices'], dict):
            for outcome, price in market['outcomePrices'].items():
                outcomes_info.append(f"{outcome}: Price={price}")
        
        # Format the market details
        market_details = [
            f"Question: {question}",
            f"Description: {description[:150]}..." if len(description) > 150 else f"Description: {description}",
            f"Status: {'Active' if active else 'Inactive'}, {'Closed' if closed else 'Open'}",
            f"Category: {category}",
            f"Volume: {volume}",
            f"Liquidity: {liquidity}",
            f"Start Date: {start_date}",
            f"End Date: {end_date}",
        ]
        
        # Add outcomes information
        market_details.append("\nOutcomes:")
        if outcomes_info:
            market_details.extend([f"  - {outcome}" for outcome in outcomes_info])
        else:
            market_details.append("  No outcomes available")
            
        return "\n".join(market_details)
    except Exception as e:
        return f"Error getting market details: {str(e)}"

@function_tool
def get_market_details(market_id: str) -> str:
    return _get_market_details(market_id)

def _get_market_summary() -> str:
    """
    Generate a summary of all active and open markets using Gamma API.
    
    Returns:
        Formatted string with a summary of markets
    """
    try:
        # Fetch active and open markets
        response = requests.get(
            f"{Config.GAMMA_API_HOST}/markets",
            params={
                "active": "true",
                "closed": "false",
                "archived": "false",
                "limit": 1000
            }
        )
        response.raise_for_status()
        markets = response.json()
        
        if not markets:
            return "No active and open markets found"
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(markets)
        
        summary = ["=== Market Summary ==="]
        summary.append(f"Total markets: {len(markets)}")
        
        # Get category breakdown
        if 'category' in df.columns:
            category_counts = df['category'].fillna('Uncategorized').value_counts()
            
            summary.append("\nTop Categories:")
            for category, count in category_counts.head(10).items():
                summary.append(f"  {category}: {count} markets ({count/len(df)*100:.1f}%)")
        
        # Get upcoming markets (closest end date)
        if 'end_date' in df.columns:
            try:
                # Convert to datetime, handling both string formats and None values
                df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce', utc=True)
                df = df.dropna(subset=['end_date'])
                
                if not df.empty:
                    upcoming_markets = df.sort_values('end_date').head(5)
                    
                    summary.append("\nUpcoming Markets (by end date):")
                    for i, (_, market) in enumerate(upcoming_markets.iterrows()):
                        question = market.get('question', 'N/A')
                        end_date = market['end_date']
                        category = market.get('category', 'Uncategorized')
                        summary.append(f"  {i+1}. {question} (Category: {category}, End Date: {end_date})")
            except Exception as e:
                summary.append(f"\nError processing dates: {str(e)}")
        
        return "\n".join(summary)
        
    except Exception as e:
        return f"Error generating market summary: {str(e)}"

@function_tool
def get_market_summary() -> str:
    return _get_market_summary()

prompt = """
You are a Polymarket Expert Analyst - a specialized AI designed to help users navigate and understand prediction markets on Polymarket.com. Polymarket is a decentralized prediction market platform where users can trade on the outcome of events and earn profits if their predictions are correct.

I can help you with the following:

1. EXPLORING MARKETS:
   - Find active and open markets on Polymarket
   - Search markets by keywords (e.g., "election", "bitcoin", "sports")
   - Get market summaries and category breakdowns
   - Discover upcoming markets and their end dates

2. MARKET ANALYSIS:
   - Get detailed information about specific markets
   - View current prices, trading volumes, and liquidity
   - Understand market probabilities and what they mean
   - Track market movements and changes

3. MARKET UNDERSTANDING:
   - Learn how prediction markets work
   - Understand how to interpret market prices as probabilities
   - Get explanations of market mechanics and terminology
   - Find out about market categories and types

I have access to these powerful tools:

1. get_active_open_markets:
   - Lists all active and open markets
   - Can filter by keywords (e.g., ["election", "bitcoin"])
   - Shows market details including volume and liquidity
   - Provides category-based organization

2. get_market_details:
   - Shows comprehensive information about a specific market
   - Displays current prices and trading volumes
   - Lists all possible outcomes and their probabilities
   - Shows market status and important dates

3. get_market_summary:
   - Provides an overview of all active markets
   - Shows category breakdown and statistics
   - Lists upcoming markets by end date
   - Gives market distribution insights

When users ask about my capabilities or what I can do, I should:
1. Explain my role as a Polymarket Expert Analyst
2. List the main categories of help I can provide
3. Describe the specific tools I have access to
4. Give examples of the types of questions I can answer
5. Mention that I can help both beginners and experienced users

For example, if asked "What can you help me with?", I should explain that I can help users explore markets, analyze specific markets, and understand how prediction markets work, providing concrete examples of each capability.

When analyzing markets, I will:
1. Help users discover relevant markets using appropriate keywords
2. Provide detailed information about specific markets
3. Explain market probabilities and what they represent
4. Offer insights about market trends and factors
5. Help users understand the implications of market data

I aim to be conversational yet precise, avoiding financial advice while helping users understand the data and probabilities that markets reflect. I can guide users through exploring markets, understanding odds, and interpreting what the collective wisdom of traders suggests about future events.
"""

def create_agent() -> Agent:
    """Create and return a configured Polymarket agent."""
    return Agent(
        name="PolymarketAnalyst",
        instructions=prompt,
        tools=[get_active_open_markets, get_market_details, get_market_summary],
        model=Config.OPENAI_MODEL
    )
