from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from dotenv import load_dotenv
import os
import requests
from datetime import datetime

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

# Initialize tools
tools = [get_news_headlines]

# Initialize the model with a specific prompt
system_prompt = """You are Ron Burgundy, a charismatic news anchor. Your task is to present news headlines 
in an engaging and professional manner, while maintaining your signature style. When users ask for news, 
use the get_news_headlines tool to fetch relevant information. Always introduce the news with your 
signature catchphrase 'I'm Ron Burgundy, and this is the news!' and end with 'Stay classy, San Diego!'

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

def get_response(question: str, thread_id: str = "news_demo") -> dict:
    """
    Get a response from the news agent for a given question.
    
    Args:
        question (str): The user's question about news
        thread_id (str): Thread identifier for the conversation
        
    Returns:
        dict: The final state containing the conversation
    """
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
    final_state = get_response(question)
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")
