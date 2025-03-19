import streamlit as st
import requests
from typing import Dict, Any

# Configure the page
st.set_page_config(
    page_title="AI Agents Test UI",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_endpoint" not in st.session_state:
    st.session_state.selected_endpoint = "CEX Aggregator"

# Define predefined questions for each agent
AGENT_QUESTIONS = {
    "CEX Aggregator": [
        "What exchanges are available?",
        "Show me my balance on Binance",
        "What is the price of BTC/USDT on Bybit?"
    ],
    "Alpaca Trader": [
        "Show me my account information",
        "Show me my current positions",
        "Place a market order to buy 1 share of INTL"
    ]
}

def normalize_agent_name(agent_name: str) -> str:
    """
    Normalize agent name to lowercase and replace spaces with hyphens
    """
    return agent_name.lower().replace(" ", "-")

def send_message(message: str, endpoint_url: str) -> Dict[Any, Any]:
    """
    Send message to the selected API endpoint
    """
    # Prepare the request payload matching ChatRequest schema
    payload = {
        "input": message,
        "history": [],
        "config": {
            "streaming": False,
            "thread_id": "test_thread"
        }
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
        "CEX Aggregator": "https://cex-aggregator-agent.fly.dev",
        "Alpaca Trader": "https://alpaca-agent.fly.dev"
    }
    
    selected_endpoint = st.radio(
        "Select Agent",
        options=list(endpoints.keys()),
        key="endpoint_selector"
    )
    
    # Display current endpoint URL
    st.code(endpoints[selected_endpoint], language="text")
    
    # Display predefined questions for the selected agent
    if selected_endpoint in AGENT_QUESTIONS:
        st.markdown("---")
        st.markdown("### Example Questions")
        for question in AGENT_QUESTIONS[selected_endpoint]:
            if st.button(question):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": question})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(question)
                
                # Show thinking message and get response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("🤔 Thinking...")
                    
                    try:
                        # Send message to API
                        response = send_message(question, endpoints[selected_endpoint])
                        
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
                
                st.rerun()

# Main chat interface
st.title("🤖 AI Agents API Tester")

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
