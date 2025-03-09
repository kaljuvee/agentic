from typing import Literal
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode, create_react_agent
from dotenv import load_dotenv
import os
from langchain.tools import DuckDuckGoSearchRun

# Load environment variables
load_dotenv()

# Define search tool
@tool
def web_search(query: str) -> str:
    """Search the web for information about a query."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

@tool
def convert_temperature(temp_str: str, to_unit: str) -> str:
    """Convert temperature between Fahrenheit and Celsius."""
    try:
        # Clean up the input string - remove spaces and handle various formats
        temp_str = temp_str.strip().upper().replace(" ", "")
        
        # Extract number using more flexible parsing
        import re
        number_match = re.search(r'(-?\d+\.?\d*)', temp_str)
        if not number_match:
            return "Could not find temperature value"
        
        temp = float(number_match.group(1))
        
        # Determine input unit
        if any(f in temp_str for f in ['F', '°F']):
            input_unit = 'F'
        elif any(c in temp_str for c in ['C', '°C']):
            input_unit = 'C'
        else:
            return "Could not determine temperature unit"
        
        # Convert based on input and target units
        to_unit = to_unit.strip().upper()
        if input_unit == 'F' and to_unit.startswith('C'):
            result = (temp - 32) * 5/9
            return f"{result:.1f}°C"
        elif input_unit == 'C' and to_unit.startswith('F'):
            result = (temp * 9/5) + 32
            return f"{result:.1f}°F"
        elif input_unit == to_unit:
            return f"{temp:.1f}°{input_unit}"
        else:
            return "Invalid conversion request"
    except Exception as e:
        return f"Error converting temperature: {str(e)}"

# Initialize tools
tools = [web_search, convert_temperature]

# Initialize the model
model = ChatAnthropic(
    model=os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-5-sonnet-latest"),
    temperature=0,
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
).bind_tools(tools)

tool_node = ToolNode(tools)

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
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# Save graph visualization
#workflow.get_graph().draw_mermaid_png("graph.png")

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
            "content": "What is the weather in New York today? Convert it to Celsius if it's in Fahrenheit."
        }]
    }
    
    final_state = app.invoke(
        initial_message,
        config={"configurable": {"thread_id": "weather_demo"}}
    )
    
    # Print the conversation
    for message in final_state["messages"]:
        print(f"\n{message.type.upper()}: {message.content}")
