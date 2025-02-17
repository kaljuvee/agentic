import streamlit as st
import requests
from typing import Dict, Any

# Configure the page
st.set_page_config(
    page_title="Zuvu AI Agents API Tester",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_endpoint" not in st.session_state:
    st.session_state.selected_endpoint = "Production"

def normalize_agent_name(agent_name: str) -> str:
    """
    Normalize agent name to lowercase and replace spaces with hyphens
    """
    return agent_name.lower().replace(" ", "-")

def send_message(message: str, endpoint_url: str) -> Dict[Any, Any]:
    """
    Send message to the selected API endpoint
    """
    # Normalize the agent name before sending
    normalized_agent = normalize_agent_name(st.session_state.agent_selector)
    
    payload = {
        "query": message,
        "agent": normalized_agent
    }
    
    try:
        response = requests.post(endpoint_url + "/chat", json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return {"response": "Error: Failed to get response from the server"}

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Endpoint selector
    endpoints = {
        "Production": "https://agentic-dcjz.onrender.com",
        "Local": "http://localhost:5000"
    }
    
    # Add agent selector
    agents = [
        "Anchorman",
        "Sevro",
        "Sous-Chef",
        "BonVoyage",
        "JRR Token",
        "ChessBuddy",
    ]
    
    selected_agent = st.selectbox(
        "Select Agent",
        options=agents,
        key="agent_selector"
    )
    
    selected_endpoint = st.radio(
        "Select API Endpoint",
        options=list(endpoints.keys()),
        key="endpoint_selector"
    )
    
    # Display current endpoint URL
    st.code(endpoints[selected_endpoint], language="text")
    
    # Add some information about the agents
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    Learn more about the available agents and their capabilities in the 
    [Agent Catalogue Documentation](https://github.com/ZuvuFoundation/agent-catalogue/blob/main/documentation/agent_ideas.md)
    """)

# Main chat interface
st.title("🤖 Zuvu AI Agents API Tester")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Show thinking message
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Thinking...")
        
        try:
            # Send message to API
            response = send_message(prompt, endpoints[selected_endpoint])
            
            # Update chat history with response
            if response and "response" in response:
                message_placeholder.markdown(response["response"])
                st.session_state.messages.append(
                    {"role": "assistant", "content": response["response"]}
                )
            else:
                message_placeholder.markdown("❌ Error: Invalid response from server")
                
        except Exception as e:
            message_placeholder.markdown(f"❌ Error: {str(e)}")

# Add a clear button
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()
