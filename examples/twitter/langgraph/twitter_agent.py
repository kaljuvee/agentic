from typing import Literal, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from dotenv import load_dotenv
import os
import tweepy
from datetime import datetime
import requests

# Load environment variables
load_dotenv()

NEWS_API_URL = "https://newsapi.org/v2"

@tool
def get_news_headlines(category: str = None, query: str = None) -> str:
    """
    Get news headlines from NewsAPI. 
    Parameters:
        category: Optional category (business, technology, sports, etc.)
        query: Optional search query
    Returns: String containing relevant news headlines
    """
    try:
        params = {
            'apiKey': os.getenv("NEWS_API_KEY"),
            'language': 'en',
        }
        
        if category:
            # For category-based search
            params['category'] = category
            endpoint = f"{NEWS_API_URL}/top-headlines"
        else:
            # For keyword-based search
            params['q'] = query if query else 'headlines'
            endpoint = f"{NEWS_API_URL}/everything"
            params['sortBy'] = 'publishedAt'
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        articles = response.json().get('articles', [])
        if not articles:
            return "No news articles found."
        
        # Format the news headlines
        formatted_news = "Here are the latest headlines:\n\n"
        for idx, article in enumerate(articles[:5], 1):
            formatted_news += f"{idx}. {article['title']}\n"
            formatted_news += f"   Source: {article['source']['name']}\n"
            formatted_news += f"   Description: {article['description']}\n\n"
            
        return formatted_news
        
    except Exception as e:
        return f"Error fetching news: {str(e)}"

@tool
def post_tweet(message: str) -> str:
    """
    Post a message to Twitter.
    Parameters:
        message: The message to post (max 200 characters)
    Returns: Status of the post
    """
    try:
        # Check character limit
        if len(message) > 200:
            return f"Error: Tweet exceeds 200 character limit. Current length: {len(message)}"
            
        # Initialize client with v2 authentication
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_KEY_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Post tweet
        response = client.create_tweet(text=message)
        tweet_id = response.data['id']
        tweet_url = f"https://twitter.com/user/status/{tweet_id}"
        return f"Successfully posted to Twitter! Tweet URL: {tweet_url}"
    
    except Exception as e:
        return f"Error posting to Twitter: {str(e)}"

# Initialize tools
tools = [get_news_headlines, post_tweet]

# Initialize the model with a specific prompt
system_prompt = """You are a helpful Twitter assistant that can fetch news and post tweets.
Your task is to help users share interesting news on Twitter.

When posting tweets:
1. First get the latest news using get_news_headlines with appropriate category or query
2. Summarize the most interesting headline(s) into a tweet
3. IMPORTANT: Keep tweets under 200 characters (not 280)
4. Keep the tone professional but engaging
5. Add relevant context when needed
6. Use the post_tweet tool to share the summary

Remember to:
1. Always check the news first before posting
2. Create very concise summaries (under 200 chars)
3. Maintain a professional tone
4. Respect Twitter's platform guidelines
5. Focus on the most impactful headline if multiple exist
6. Include the news source when possible

Tweet Format Tips:
- Be direct and clear
- Remove unnecessary words
- Use numbers instead of writing them out
- Avoid redundant hashtags
- Keep URLs short if needed
- Format: "Headline summary - via @NewsSource"
"""

# Initialize the model
model = ChatAnthropic(
    model=os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-latest"),
    temperature=0.7,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
).bind_tools(tools)

tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Determine if we should continue using tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: MessagesState):
    """Call the model with the current state."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Create and configure the graph
workflow = StateGraph(MessagesState)

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
app = workflow.compile(checkpointer=checkpointer)

def get_response(
    question: str, 
    thread_id: str = "twitter_demo",
    username: Optional[str] = None
) -> dict:
    """
    Get a response from the Twitter agent for a given question.
    
    Args:
        question (str): The user's question or request
        thread_id (str): Thread identifier for the conversation
        username (str, optional): Twitter username for timeline requests
        
    Returns:
        dict: The final state containing the conversation
    """
    if username:
        question = f"{question} for user @{username}"
        
    initial_message = {
        "messages": [{
            "role": "user",
            "content": question
        }]
    }
    
    return app.invoke(
        initial_message,
        config={"configurable": {"thread_id": thread_id}}
    )

if __name__ == "__main__":
    # Test the agent directly
    test_cases = [
        "Post a tweet saying 'Testing the Twitter API integration!'",
        "Show me the recent tweets from @OpenAI"
    ]
    
    for question in test_cases:
        print(f"\nTesting: {question}")
        print("=" * 50)
        
        final_state = get_response(question)
        
        # Print the conversation
        for message in final_state["messages"]:
            print(f"\n{message.type.upper()}: {message.content}")
