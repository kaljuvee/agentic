from typing import Literal, Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from arcadepy import Arcade

#https://github.com/langchain-ai/langgraph/blob/main/docs/docs/concepts/low_level.md
# Load environment variables
load_dotenv()

# Define the state type
class SocialMediaState(TypedDict):
    messages: Annotated[list, add_messages]
    thread_id: Optional[str]

# Initialize Arcade client
client = Arcade(api_key=os.getenv("ARCADE_API_KEY"))

@tool
def post_to_linkedin(content: str) -> str:
    """
    Post content to LinkedIn.
    
    Args:
        content (str): The content to post
    """
    try:
        input_data = {
            "text": content,
            "user_id": os.getenv("LINKEDIN_USER_ID")
        }
        
        # Add organization ID if posting as organization
        if os.getenv("POST_TO_LINKEDIN_ORGANIZATION", "false").lower() == "true":
            input_data["organization_id"] = os.getenv("LINKEDIN_ORGANIZATION_ID")
        
        response = client.tools.execute(
            tool_name="Linkedin.CreateTextPost@0.1.10",
            input=input_data,
            user_id=os.getenv("LINKEDIN_USER_ID")
        )
        return f"Successfully posted to LinkedIn: {response.output.value}"
    except Exception as e:
        return f"Error posting to LinkedIn: {str(e)}"

# Initialize tools
tools = [post_to_linkedin]

# Initialize the model with a specific prompt
system_prompt = """You are a professional social media assistant. Your task is to help users post content 
to LinkedIn using the Arcade.dev API.

You have access to the following tools:
1. post_to_linkedin: Post content to LinkedIn

When posting content:
1. Ensure the content is appropriate for the platform
2. Format LinkedIn posts professionally
3. Provide clear feedback about the posting status

Remember to:
1. Be professional and engaging
2. Consider platform-specific best practices
3. Handle errors gracefully
4. Confirm successful posts
"""

# Initialize the model
model = ChatOpenAI(
    model=os.getenv("OPENAI_MODEL_NAME", "gpt-4"),
    temperature=0.7,
    streaming=True,
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

def call_model(state: SocialMediaState):
    """Call the model with the current state."""
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# Create and configure the graph
def create_graph():
    """Create and configure the LangGraph for the social media agent."""
    # Create the graph
    workflow = StateGraph(SocialMediaState)
    
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
    thread_id: str = "social_media_demo"
) -> str:
    """
    Stream a response from the social media agent for a given question.
    
    Args:
        question (str): The user's social media-related question
        thread_id (str): Thread identifier for the conversation
        
    Returns:
        An async generator that yields streaming responses
    """
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
    thread_id: str = "social_media_demo"
) -> dict:
    """
    Get a response from the social media agent for a given question.
    
    Args:
        question (str): The user's social media-related question
        thread_id (str): Thread identifier for the conversation
        
    Returns:
        dict: The final state containing the conversation
    """
    initial_message = {
        "messages": [{
            "role": "user",
            "content": question
        }],
        "thread_id": thread_id
    }
    
    return graph.invoke(
        initial_message,
        config={"configurable": {"thread_id": thread_id}}
    )

if __name__ == "__main__":
    # Test the agent directly
    question = "Post 'Hello World!' to LinkedIn"
    final_state = get_response(question)
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")