import streamlit as st
import requests
from typing import Dict, Any
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables right after imports
load_dotenv()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_endpoint" not in st.session_state:
    st.session_state.selected_endpoint = "CEX Aggregator"

# Configure the page
st.set_page_config(
    page_title="AI Agents Test UI",
    page_icon="🤖",
    layout="wide"
)

# Define predefined questions for each agent
AGENT_QUESTIONS = {
    "CEX Aggregator": [
        "What exchanges are available?",
        "Show me my balance on Bitstamp",
        "What is the price of BTC/USDC on Binance?"
    ],
    "Alpaca Trader": [
        "Show me my account information",
        "Show me my current positions",
        "Place a market order to buy 1 share of INTL"
    ],
    "Polymarket Agent": [
        "Show me sports markets",
        "Show me crypto markets"
    ],
    "NewsX": [
        "Comment on news on China",
        "Comment on news on the Ukraine war",
        "Comment on news on US stock market"
    ]
}

def normalize_agent_name(agent_name: str) -> str:
    """
    Normalize agent name to lowercase and replace spaces with hyphens
    """
    return agent_name.lower().replace(" ", "-")

def format_positions_markdown(text: str) -> str:
    """
    Clean up and format markdown for position responses to ensure proper rendering in Streamlit.
    """
    # Replace '---' with horizontal rules and double newlines
    text = text.replace('---', '\n\n---\n\n')
    # Ensure headings have double newlines before and after
    text = text.replace('###', '\n\n###')
    # Remove stray asterisks not part of markdown
    text = re.sub(r'(?<!\*)\*(?!\*)', '', text)
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def send_message(message: str, endpoint_url: str, streaming: bool = True) -> Dict[Any, Any]:
    """
    Send message to the selected API endpoint
    """
    payload = {
        "input": message,
        "history": [],
        "config": {
            "streaming": streaming,
            "thread_id": "test_thread"
        }
    }
    try:
        response = requests.post(endpoint_url + "/chat", json=payload, stream=streaming)
        response.raise_for_status()
        full_response = ""
        if streaming:
            for line in response.iter_lines():
                if line:
                    try:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            content = line_str[6:]
                            full_response += content
                    except Exception as e:
                        st.error(f"Error processing response: {str(e)}")
                        continue
            if not full_response:
                st.error("No response received from the server")
                return {"response": "Error: No response received from the server"}
            return {"response": full_response}
        else:
            return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return {"response": "Error: Failed to get response from the server"}

# Main app interface (no login required)
# Show sidebar when logged in
st.markdown(
    """
    <style>
    .stSidebar {visibility: visible;}
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Add instructions
    st.markdown("### 📝 How to Use")
    st.markdown("""
    1. **Select an Agent** below to interact with
    2. Type your message in the chat input
    3. Try the **Example Questions** below for quick testing
    """)
    
    st.markdown("---")

    # Voice toggle (placeholder for future implementation)
    st.toggle("🎤 Enable Voice Input (Coming Soon)", value=False, disabled=True)
    
    st.markdown("---")
    
    # Endpoint selector
    endpoints = {
        "CEX Aggregator": "https://cex-aggregator-agent.fly.dev",
        "Alpaca Trader": "https://alpaca-agent.fly.dev",
        "Polymarket Agent": "https://zuvu-polymarket.dev/api",
        "NewsX": "https://x-posting-agent.fly.dev"
    }
    
    selected_endpoint = st.radio(
        "Select Agent",
        options=list(endpoints.keys()),
        key="endpoint_selector"
    )
    
    # Display current endpoint URL
    st.code(endpoints[selected_endpoint], language="text")
    
    # Add streaming/non-streaming toggle, default to Non-Streaming
    streaming_mode = st.radio(
        "Response Mode",
        options=["Streaming", "Non-Streaming"],
        key="streaming_mode_selector",
        index=1  # Default to Non-Streaming
    )
    is_streaming = streaming_mode == "Streaming"
    st.session_state.streaming_mode = is_streaming
    
    # Display predefined questions for the selected agent
    if selected_endpoint in AGENT_QUESTIONS:
        st.markdown("---")
        st.markdown("### Example Questions")
        for question in AGENT_QUESTIONS[selected_endpoint]:
            if st.button(question):
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("🤔 Thinking...")
                    try:
                        response = send_message(
                            question,
                            endpoints[selected_endpoint],
                            streaming=st.session_state.get("streaming_mode", True)
                        )
                        if response and "response" in response:
                            formatted_response = format_positions_markdown(response["response"])
                            message_placeholder.markdown(formatted_response)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": response["response"]}
                            )
                        else:
                            message_placeholder.markdown("❌ Error: Invalid response from server")
                    except Exception as e:
                        message_placeholder.markdown(f"❌ Error: {str(e)}")
                st.rerun()
    
    # Add a clear button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    # Add a refresh button to restart the session
    if st.button("Refresh"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main chat interface
st.title("🤖 AI Agents API Tester")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤔 Thinking...")
        try:
            response = send_message(
                prompt,
                endpoints[selected_endpoint],
                streaming=st.session_state.get("streaming_mode", True)
            )
            if response and "response" in response:
                formatted_response = format_positions_markdown(response["response"])
                message_placeholder.markdown(formatted_response)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response["response"]}
                )
            else:
                message_placeholder.markdown("❌ Error: Invalid response from server")
        except Exception as e:
            message_placeholder.markdown(f"❌ Error: {str(e)}")
