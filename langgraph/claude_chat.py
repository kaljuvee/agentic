from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define weather tool
@tool
def get_weather(location: str) -> str:
    """Get the weather for a specific location."""
    # This is a mock implementation
    weather_data = {
        "new york": "72°F and sunny",
        "san francisco": "65°F and foggy",
        "london": "60°F and rainy",
        "tokyo": "75°F and cloudy"
    }
    return weather_data.get(location.lower(), "Weather data not available for this location")

@tool
def convert_temperature(temp_str: str, to_unit: str) -> str:
    """Convert temperature between Fahrenheit and Celsius."""
    try:
        # Extract number from string like "72°F"
        temp = float(temp_str.split('°')[0])
        if to_unit.upper() == "C" and "°F" in temp_str:
            return f"{(temp - 32) * 5/9:.1f}°C"
        elif to_unit.upper() == "F" and "°C" in temp_str:
            return f"{(temp * 9/5) + 32:.1f}°F"
        else:
            return "Invalid conversion request"
    except:
        return "Invalid temperature format"

# Initialize tools
tools = [get_weather, convert_temperature]
tool_node = ToolNode(tools)

# Initialize the model with tools
model = ChatAnthropic(
    model=os.getenv("ANTHROPIC_MODEL_NAME"),
    temperature=0,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")  # Load from environment variable
).bind_tools(tools)

# Define routing logic
def should_continue(state: MessagesState) -> Literal["tools", END]:
    """Determine if we should continue using tools or end the conversation."""
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Define model calling logic
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
)
workflow.add_edge("tools", "agent")

# Initialize memory
checkpointer = MemorySaver()

# Compile the graph
app = workflow.compile(checkpointer=checkpointer)

# Example usage
if __name__ == "__main__":
    # Test the agent
    initial_message = {
        "messages": [{
            "role": "user",
            "content": "What's the weather like in San Francisco? Can you convert it to Celsius?"
        }]
    }
    
    final_state = app.invoke(
        initial_message,
        config={"configurable": {"thread_id": "weather_demo"}}
    )
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")
