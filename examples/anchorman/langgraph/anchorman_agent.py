from typing import Literal, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from dotenv import load_dotenv
import os
import requests
from datetime import datetime
import tweepy

#https://github.com/langchain-ai/langgraph/blob/main/docs/docs/concepts/low_level.md
# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
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
            'apiKey': NEWS_API_KEY,
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
def post_to_twitter(message: str) -> str:
    """
    Post a message to Twitter.
    Parameters:
        message: The message to post (max 280 characters)
    Returns: Status of the post
    """
    try:
        # Initialize Twitter client
        auth = tweepy.OAuthHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET")
        )
        auth.set_access_token(
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        twitter_client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Post tweet
        response = twitter_client.create_tweet(text=message)
        return f"Successfully posted to Twitter! Tweet ID: {response.data['id']}"
    
    except Exception as e:
        return f"Error posting to Twitter: {str(e)}"

# Initialize tools
tools = [get_news_headlines, post_to_twitter]

# Initialize the model with a specific prompt
system_prompt = """You are Ron Burgundy, a charismatic news anchor. Your task is to present news headlines 
in an engaging and professional manner, while maintaining your signature style. When users ask for news, 
use the get_news_headlines tool to fetch relevant information and optionally post to Twitter.

Always introduce the news with your signature catchphrase 'I'm Ron Burgundy, and this is the news!' 
and end with 'Stay classy, San Diego!'

When asked to post to Twitter:
1. Create a brief, engaging summary of the news (max 280 characters)
2. Use your Ron Burgundy style but keep it professional
3. Use the post_to_twitter tool to share the summary

Remember to:
1. Use the appropriate tool to fetch news based on the user's request
2. Present the news in a clear and engaging manner
3. Maintain your professional news anchor persona
4. Add brief, relevant commentary between headlines
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
    thread_id: str = "news_demo",
    post_to_twitter: bool = False
) -> dict:
    """
    Get a response from the news agent for a given question and optionally post to Twitter.
    
    Args:
        question (str): The user's question about news
        thread_id (str): Thread identifier for the conversation
        post_to_twitter (bool): Whether to post the news summary to Twitter
        
    Returns:
        dict: The final state containing the conversation
    """
    if post_to_twitter:
        question = f"{question} Please also create a brief summary and post it to Twitter."
        
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
    question = "What are the top business headlines today?"
    final_state = get_response(question, post_to_twitter=True)
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")
