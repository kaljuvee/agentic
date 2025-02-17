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

# Load environment variables
load_dotenv()

@tool
def post_tweet(message: str) -> str:
    """
    Post a message to Twitter.
    Parameters:
        message: The message to post (max 280 characters)
    Returns: Status of the post
    """
    try:
        # Initialize Twitter client
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Post tweet
        response = client.create_tweet(text=message)
        return f"Successfully posted to Twitter! Tweet ID: {response.data['id']}"
    
    except Exception as e:
        return f"Error posting to Twitter: {str(e)}"

@tool
def get_user_timeline(username: str, count: int = 5) -> str:
    """
    Get recent tweets from a user's timeline.
    Parameters:
        username: Twitter username (without @)
        count: Number of tweets to retrieve (default: 5)
    Returns: String containing recent tweets
    """
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Get user's tweets
        tweets = client.get_users_tweets(
            username,
            max_results=count,
            exclude=['retweets', 'replies']
        )
        
        if not tweets.data:
            return f"No tweets found for user @{username}"
        
        formatted_tweets = f"Recent tweets from @{username}:\n\n"
        for tweet in tweets.data:
            formatted_tweets += f"- {tweet.text}\n\n"
            
        return formatted_tweets
        
    except Exception as e:
        return f"Error fetching tweets: {str(e)}"

# Initialize tools
tools = [post_tweet, get_user_timeline]

# Initialize the model with a specific prompt
system_prompt = """You are a helpful Twitter assistant that can post tweets and read user timelines.
Your task is to help users interact with Twitter in a natural way.

When posting tweets:
1. Ensure the message is within Twitter's 280 character limit
2. Keep the tone appropriate and professional
3. Format the message clearly

When reading timelines:
1. Present the tweets in a clear, readable format
2. Provide relevant context when needed
3. Handle any errors gracefully

Remember to:
1. Use the appropriate tool based on the user's request
2. Maintain a helpful and professional tone
3. Respect Twitter's platform guidelines
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
