from typing import Literal, Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
import tweepy
import requests
import json

# Load environment variables
load_dotenv()

NEWS_API_URL = "https://newsapi.org/v2"

# Define the state type
class NewsXState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: Optional[str]

@tool
def news_headlines(category: str = None, query: str = None) -> str:
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
        
        # Get just the top headline for neutral commentary
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
            
        # Add NewsX prefix if not present
        if not message.startswith("NewsX:"):
            message = f"NewsX: {message}"
            
        # Print debug info
        print(f"Attempting to post tweet: {message}")
        
        # Check if Twitter credentials are available
        if not os.getenv("TWITTER_API_KEY") or not os.getenv("TWITTER_API_KEY_SECRET"):
            return "Error: Twitter API credentials not found in environment variables"
            
        # Initialize client with v2 authentication
        client = tweepy.Client(
            bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_KEY_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # Get the user's username for the tweet URL
        username = "user"  # Default username
        try:
            user_info = client.get_me()
            if hasattr(user_info, 'data') and user_info.data and hasattr(user_info.data, 'username'):
                username = user_info.data.username
            elif isinstance(user_info, dict) and 'data' in user_info and 'username' in user_info['data']:
                username = user_info['data']['username']
        except Exception as e:
            print(f"Warning: Could not get username: {str(e)}")
            # Continue with default username
        
        # Post tweet
        response = client.create_tweet(text=message)
        
        # Debug the response
        print(f"Twitter API response: {response}")
        
        # Handle different response formats
        tweet_id = None
        
        if hasattr(response, 'data') and response.data:
            if hasattr(response.data, 'id'):
                tweet_id = response.data.id
            elif isinstance(response.data, dict) and 'id' in response.data:
                tweet_id = response.data['id']
        elif isinstance(response, dict) and 'data' in response:
            if isinstance(response['data'], dict) and 'id' in response['data']:
                tweet_id = response['data']['id']
        
        if not tweet_id:
            return "Error: Could not extract tweet ID from Twitter API response"
            
        tweet_url = f"https://x.com/{username}/status/{tweet_id}"
        return f"Successfully posted to Twitter! Tweet URL: {tweet_url}"
    
    except tweepy.errors.Unauthorized as e:
        print(f"Twitter authentication error: {str(e)}")
        return f"Error: Twitter authentication failed. Please check your credentials. Details: {str(e)}"
    except tweepy.errors.BadRequest as e:
        print(f"Twitter bad request error: {str(e)}")
        return f"Error: Bad request to Twitter API. Details: {str(e)}"
    except tweepy.errors.Forbidden as e:
        print(f"Twitter forbidden error: {str(e)}")
        return f"Error: Twitter API access forbidden. Your app may not have write permissions. Details: {str(e)}"
    except Exception as e:
        print(f"Twitter posting error: {str(e)}")
        return f"Error posting to Twitter: {str(e)}"

# Initialize tools
tools = [news_headlines, post_tweet]

# Initialize the model with a specific prompt
system_prompt = """You are NewsX, a Twitter bot that shares news headlines in a neutral, professional style similar to Bloomberg or Reuters.
Your task is to transform news into concise, factual posts that inform readers about current events.

IMPORTANT: You MUST follow this exact process for EVERY request:
1. First use the news_headlines tool with the user's specified topic/query to get the latest news
2. Analyze the headline and create a neutral, professional commentary
3. Use the post_tweet tool to share your commentary - this step is MANDATORY

When creating posts:
1. Take the headline and transform it into a concise, factual statement
2. IMPORTANT: Keep tweets under 270 characters
3. Use clear, precise language without bias or opinion
4. Focus on accuracy and clarity
5. Include relevant context when necessary

Style Guidelines:
- Use formal, professional language
- Avoid sensationalism or emotional language
- Present facts without commentary or opinion
- Use straightforward sentence structure
- End with #NewsX

Example formats:
"US GDP grows 2.5% in Q2, exceeding analyst expectations of 2.1%. Federal Reserve signals potential rate adjustment in response to economic indicators. #NewsX"

Remember:
1. Focus on ONE main headline
2. Keep it under 270 chars
3. Stay neutral and factual
4. Make it informative and clear
5. Always verify news before posting
6. ALWAYS use the post_tweet tool to share your commentary
"""

# Initialize the model
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o"),
    temperature=0.7,
    streaming=True,
    openai_api_key=os.getenv("OPENAI_API_KEY")
).bind_tools(tools)

tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Determine if we should continue using tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: NewsXState):
    """Call the model with the current state."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Create and configure the graph
def create_graph():
    """Create and configure the LangGraph for the NewsX agent."""
    # Create the graph
    workflow = StateGraph(NewsXState)
    
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
    return workflow.compile(checkpointer=checkpointer)

# Create the graph
graph = create_graph()

# Define the output nodes
output_nodes = ["agent"]

async def stream_response(
    question: str, 
    thread_id: str = "newsx_demo",
    username: Optional[str] = None,
    auto_post: bool = True
):
    """
    Stream a response from the NewsX agent for a given question.
    
    Args:
        question (str): The user's question or request
        thread_id (str): Thread identifier for the conversation
        username (str, optional): Twitter username for timeline requests
        auto_post (bool): Whether to automatically ensure a post is made
        
    Returns:
        An async generator that yields streaming responses
    """
    if username:
        question = f"{question} for user @{username}"
    
    # Ensure the question is properly formatted for news
    if not question.lower().startswith("news on"):
        question = f"news on {question}"
    
    state = {
        "messages": [{"role": "user", "content": question}],
        "thread_id": thread_id
    }
    
    async for stream_mode, chunk in graph.astream(
        state, 
        stream_mode=["messages"],
        config={"configurable": {"thread_id": thread_id}}
    ):
        if stream_mode == "messages":
            msg, metadata = chunk
            if msg.content and metadata["langgraph_node"] in output_nodes:
                yield f"data: {msg.content}\n\n"

def get_response(
    question: str, 
    thread_id: str = "newsx_demo",
    username: Optional[str] = None,
    auto_post: bool = True
) -> tuple:
    """
    Get a response from the NewsX agent for a given question and automatically post to Twitter.
    
    Args:
        question (str): The user's question or request
        thread_id (str): Thread identifier for the conversation
        username (str, optional): Twitter username for timeline requests
        auto_post (bool): Whether to automatically ensure a post is made
        
    Returns:
        tuple: (response_text, tweet_url) where response_text is the agent's response and
               tweet_url is the URL of the posted tweet (or None if no tweet was posted)
    """
    if username:
        question = f"{question} for user @{username}"
    
    # Ensure the question is properly formatted for news
    if not question.lower().startswith("news on"):
        question = f"news on {question}"
        
    initial_message = {
        "messages": [{
            "role": "user",
            "content": question
        }],
        "thread_id": thread_id
    }
    
    # Get the response from the agent
    final_state = graph.invoke(
        initial_message,
        config={"configurable": {"thread_id": thread_id}}
    )
    
    # Extract tweet URL if available
    tweet_url = None
    tweet_attempted = False
    tweet_content = None
    
    for message in final_state["messages"]:
        # Check if message is a tool call for post_tweet
        is_tool = False
        tool_name = None
        tool_content = None
        tool_input = None
        
        # Handle different message formats
        if hasattr(message, 'type') and message.type == "tool":
            is_tool = True
            if hasattr(message, 'name'):
                tool_name = message.name
            if hasattr(message, 'content'):
                tool_content = message.content
            if hasattr(message, 'input'):
                tool_input = message.input
        elif isinstance(message, dict) and message.get('type') == "tool":
            is_tool = True
            tool_name = message.get('name')
            tool_content = message.get('content')
            tool_input = message.get('input')
        
        # Process post_tweet tool calls
        if is_tool and tool_name == "post_tweet":
            tweet_attempted = True
            if tool_content and "Successfully posted" in tool_content:
                # Extract the URL from the success message
                url_start = tool_content.find("Tweet URL: ") + len("Tweet URL: ")
                tweet_url = tool_content[url_start:].strip()
                
                # Extract the tweet content from the post_tweet tool input
                if tool_input:
                    tweet_content = tool_input
                break
    
    # If auto_post is enabled and no tweet was attempted, force a post
    if auto_post and not tweet_attempted:
        # Find the news headline in the conversation
        headline = None
        for message in final_state["messages"]:
            # Check if message is a tool call for news_headlines
            is_tool = False
            tool_name = None
            tool_content = None
            
            # Handle different message formats
            if hasattr(message, 'type') and message.type == "tool":
                is_tool = True
                if hasattr(message, 'name'):
                    tool_name = message.name
                if hasattr(message, 'content'):
                    tool_content = message.content
            elif isinstance(message, dict) and message.get('type') == "tool":
                is_tool = True
                tool_name = message.get('name')
                tool_content = message.get('content')
            
            if is_tool and tool_name == "news_headlines" and tool_content:
                headline = tool_content
                break
        
        if headline:
            # Generate a simple neutral post from the headline
            try:
                # Extract the main headline
                title_start = headline.find("Top headline: ") + len("Top headline: ")
                title_end = headline.find("\n", title_start)
                title = headline[title_start:title_end].strip()
                
                # Extract the source
                source_start = headline.find("Source: ") + len("Source: ")
                source_end = headline.find("\n", source_start)
                source = headline[source_start:source_end].strip()
                
                # Create a neutral post
                post = f"{title} - {source}. #NewsX"
                if len(post) > 270:
                    post = post[:267] + "..."
                
                # Save the tweet content
                tweet_content = post
                
                # Post to Twitter
                print(f"Auto-posting tweet: {post}")
                result = post_tweet(post)
                print(f"Auto-post result: {result}")
                
                # Extract the URL if successful
                if "Successfully posted" in result:
                    url_start = result.find("Tweet URL: ") + len("Tweet URL: ")
                    tweet_url = result[url_start:].strip()
                    print(f"Extracted tweet URL: {tweet_url}")
                else:
                    print("Failed to extract tweet URL from result")
                
                # Add the result to the conversation
                final_state["messages"].append({
                    "role": "system",
                    "content": f"Auto-posted to Twitter: {result}"
                })
            except Exception as e:
                print(f"Error in auto-posting: {str(e)}")
                final_state["messages"].append({
                    "role": "system",
                    "content": f"Error auto-posting to Twitter: {str(e)}"
                })
    
    # Get the last assistant message as the response
    response_text = None
    for message in reversed(final_state["messages"]):
        # Check if message is from assistant
        is_assistant = False
        assistant_content = None
        
        # Handle different message formats
        if hasattr(message, 'type') and message.type == "assistant":
            is_assistant = True
            if hasattr(message, 'content'):
                assistant_content = message.content
        elif isinstance(message, dict) and message.get('type') == "assistant":
            is_assistant = True
            assistant_content = message.get('content')
        elif isinstance(message, dict) and message.get('role') == "assistant":
            is_assistant = True
            assistant_content = message.get('content')
        
        if is_assistant and assistant_content:
            response_text = assistant_content
            break
    
    # Construct the final response
    final_response = ""
    
    # If we have tweet content, always include it
    if tweet_content:
        # If the tweet content doesn't start with "NewsX:", add it
        if not tweet_content.startswith("NewsX:"):
            final_response += f"NewsX: {tweet_content}\n\n"
        else:
            final_response += f"{tweet_content}\n\n"
    
    # If we have an assistant response and it's not already included, add it
    if response_text and response_text.strip() and response_text not in final_response:
        final_response += response_text
    
    # If we still don't have a response, use a default message
    if not final_response.strip():
        final_response = "NewsX has processed your request."
    
    # Add the tweet URL to the response if it exists
    if tweet_url and "Tweet URL:" not in final_response:
        print(f"Adding tweet URL to response: {tweet_url}")
        final_response += f"\n\nSuccessfully posted to Twitter! Tweet URL: {tweet_url}"
    else:
        if tweet_url:
            print(f"Tweet URL already in response: {tweet_url}")
        else:
            print("No tweet URL to add to response")
    
    print(f"Final response: {final_response}")
    return final_response, tweet_url

if __name__ == "__main__":
    # Test the agent directly
    test_cases = [
        "news on president",
        "news on politics"
    ]
    
    print("\n📰 NewsX Test Session 📰")
    print("=" * 50)
    
    for question in test_cases:
        print(f"\n📰 Testing: {question}")
        print("-" * 50)
        
        response, tweet_url = get_response(question, auto_post=True)
        
        # Print the response
        print(f"\n📰 NewsX Response:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # Display tweet URL if available
        if tweet_url:
            print(f"\n🔗 Tweet URL: {tweet_url}")
            print(f"✅ Successfully posted to Twitter!")
        else:
            print("\n⚠️ No tweet was posted")
        
        print("\n" + "=" * 50)
