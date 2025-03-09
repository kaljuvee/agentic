from typing import Literal, Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

#https://github.com/langchain-ai/langgraph/blob/main/docs/docs/concepts/low_level.md
# Load environment variables
load_dotenv()

# Define the state type
class RoastState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: Optional[str]

# Initialize DuckDuckGo search
search = DuckDuckGoSearchAPIWrapper(region="wt-wt", time="d", max_results=5)

@tool
def duckduckgo_search(query: str) -> str:
    """
    Search the web for information about a person or topic.
    
    Args:
        query (str): The search query, typically a person's name or topic
        
    Returns:
        str: Search results from DuckDuckGo
    """
    try:
        results = search.run(query)
        return f"Search results for '{query}':\n\n{results}"
    except Exception as e:
        return f"Error performing search: {str(e)}"

# Initialize tools
tools = [duckduckgo_search]

# System prompt
system_prompt = """You are a comedy roast agent with a sharp wit and hilarious sense of humor. 
Your job is to create personalized roasting questions about people.

When given a name, you will:
1. Search for information about them using DuckDuckGo
2. Based on the search results, create 5 hilarious roasting questions
3. Make the questions funny but not overly mean or inappropriate
4. Focus on professional achievements, public information, or general traits
5. Avoid sensitive topics like race, religion, disabilities, or serious personal tragedies

Your roasts should be:
- Clever and witty
- Based on factual information when possible
- Playful rather than hurtful
- Appropriate for a comedy club setting

IMPORTANT: Always show your thought process by first summarizing what you learned from the search results, then create the roasting questions based on that information.

Format your response like this:
---
## What I Found About [Name]
[Summarize key information from search results]

## Roasting Questions
1. [First roasting question]
2. [Second roasting question]
3. [Third roasting question]
4. [Fourth roasting question]
5. [Fifth roasting question]
---

Remember: Good roasts are funny because they contain a kernel of truth, but are delivered with good humor.
"""

# Get model name from environment or use default
model_name = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# Initialize the model
model = ChatOpenAI(
    model=model_name,
    temperature=0.8,
    max_tokens=1024,
    openai_api_key=os.getenv("OPENAI_API_KEY")
).bind_tools(tools)

# Create tool node
tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Determine if we should continue using tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: RoastState):
    """Call the model with the current state."""
    messages = state['messages']
    
    # Add system message if it's not already there
    if not any(msg.get("type") == "system" for msg in messages):
        messages = [SystemMessage(content=system_prompt)] + messages
    
    response = model.invoke(messages)
    return {"messages": [response]}

# Create and configure the graph
def create_graph():
    """Create and configure the LangGraph for the roasting agent."""
    # Create the graph
    workflow = StateGraph(RoastState)
    
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

def get_response(
    name: str,
    thread_id: str = "roast_demo"
) -> dict:
    """
    Get a response from the roasting agent for a given name.
    
    Args:
        name (str): The name of the person to roast
        thread_id (str): Thread identifier for the conversation
        
    Returns:
        dict: The final state containing the conversation
    """
    prompt = f"Create 5 funny roasting questions for {name}. Make sure to search for information about them first."
    
    initial_message = {
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "thread_id": thread_id
    }
    
    return graph.invoke(
        initial_message,
        config={"configurable": {"thread_id": thread_id}}
    )

def get_roast_questions(name: str) -> str:
    """
    A simplified function that returns just the roast questions as a string.
    
    Args:
        name (str): The name of the person to roast
        
    Returns:
        str: The roast questions
    """
    try:
        response = get_response(name)
        
        # Extract the assistant's message
        for message in response["messages"]:
            if message.type == "assistant":
                return message.content
        
        return "Sorry, I couldn't generate roast questions at this time."
    except Exception as e:
        print(f"Error generating roast questions: {str(e)}")
        return f"Error generating roast questions: {str(e)}"

if __name__ == "__main__":
    # Test the agent directly
    name = "Elon Musk"
    roast_questions = get_roast_questions(name)
    print(f"\nRoast questions for {name}:\n")
    print(roast_questions)