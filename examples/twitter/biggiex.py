from typing import Literal, Optional
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os
import tweepy
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
            params['category'] = category
            endpoint = f"{NEWS_API_URL}/top-headlines"
        else:
            params['q'] = query if query else 'headlines'
            endpoint = f"{NEWS_API_URL}/everything"
            params['sortBy'] = 'publishedAt'
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        articles = response.json().get('articles', [])
        if not articles:
            return "No news articles found."
        
        # Get just the top headline for Biggie to rap about
        top_article = articles[0]
        headline = f"Top headline: {top_article['title']}\n"
        headline += f"Source: {top_article['source']['name']}\n"
        headline += f"Description: {top_article['description']}"
            
        return headline
        
    except Exception as e:
        return f"Error fetching news: {str(e)}"

@tool
def post_tweet(message: str) -> str:
    """
    Post a message to Twitter.
    Parameters:
        message: The message to post (max 270 characters)
    Returns: Status of the post
    """
    try:
        # Check character limit
        if len(message) > 270:
            return f"Error: Tweet exceeds 270 character limit. Current length: {len(message)}"
            
        # Add BiggieX prefix if not present
        if not message.startswith("BiggieX:"):
            message = f"BiggieX: {message}"
            
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
system_prompt = """You are BiggieX, a Twitter bot that raps news headlines in the style of The Notorious B.I.G.
Your task is to transform news into short rap verses that capture Biggie's style and flow.

Process:
1. First use get_news_headlines with the user's specified topic/query to get the latest news
2. Analyze the headline and create a Biggie-style rap about it
3. Use post_tweet to share your rap

When creating raps:
1. Take the headline and transform it into a Biggie-style rap verse
2. IMPORTANT: Keep tweets under 270 characters
3. Channel Biggie's swagger, wordplay, and rhythm
4. Keep it street but informative about the news

Biggie Style Guidelines:
- Use Biggie's signature Brooklyn slang and flow
- Include references to money, power, and street life when relevant
- Keep it smooth but hard-hitting
- Maintain Biggie's confident tone
- End with #BiggieNews

Example formats:
"Yo, check the headline from the streets of Beijing / China's GDP rising, got that economic bling / Bank accounts swelling, while the West just watching / Big Poppa called it, now the markets steady rocking #BiggieNews"

Remember:
1. Focus on ONE main headline
2. Keep it under 270 chars
3. Stay true to Biggie's style
4. Make it both informative and entertaining
5. Always verify news before spitting bars
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
    thread_id: str = "biggiex_demo",
    username: Optional[str] = None
) -> dict:
    """
    Get a response from the BiggieX agent for a given question.
    
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
        "rap on president",
        "rap on politics"
    ]
    
    print("\n🎤 BiggieX News Rap Test Session 🎤")
    print("=" * 50)
    
    for question in test_cases:
        print(f"\n📰 Testing: {question}")
        print("-" * 50)
        
        final_state = get_response(question)
        
        # Print the conversation
        for message in final_state["messages"]:
            if message.type == "assistant":
                print(f"\n🎵 BiggieX: {message.content}")
            else:
                print(f"\n👤 User: {message.content}")
        print("\n" + "=" * 50)
