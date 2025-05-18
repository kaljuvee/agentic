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
    st.session_state.selected_endpoint = "Alpaca Trader"

# Global configuration
STREAMING_ENABLED = False

# Configure the page
st.set_page_config(
    page_title="Agentic AI Demo",
    page_icon="🤖",
    layout="wide"
)

def normalize_agent_name(agent_name: str) -> str:
    """
    Normalize agent name to lowercase and replace spaces with hyphens
    """
    return agent_name.lower().replace(" ", "-")

def send_message(message: str, endpoint_url: str, streaming: bool = STREAMING_ENABLED) -> Dict[Any, Any]:
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
        if streaming:
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        line_str = line.decode('utf-8')
                        if line_str.startswith('data: '):
                            content = line_str[6:]
                            if content.strip():
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
    # Keep the agent selection and endpoint URL display
    endpoints = {
        "Alpaca Trader": "https://alpaca-agent.fly.dev",
        "CEX Aggregator": "https://cex-aggregator-agent.fly.dev",
        "Polymarket Agent": "https://zuvu-polymarket-agent.fly.dev/chat",
        "NewsX": "https://x-posting-agent.fly.dev"
    }
    
    selected_endpoint = st.radio(
        "Select Agent",
        options=list(endpoints.keys()),
        key="endpoint_selector"
    )
    st.session_state.selected_endpoint = selected_endpoint
    st.code(endpoints[selected_endpoint], language="text")
    
    # Add a divider and refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Chat", use_container_width=True):
        st.session_state.messages = []

# Main chat interface
st.title(f"🤖 {selected_endpoint}")

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
                streaming=STREAMING_ENABLED
            )
            if response and "response" in response:
                message_placeholder.markdown(response["response"])
                st.session_state.messages.append(
                    {"role": "assistant", "content": response["response"]}
                )
            else:
                message_placeholder.markdown("❌ Error: Invalid response from server")
        except Exception as e:
            message_placeholder.markdown(f"❌ Error: {str(e)}")

# In the main chat interface, after the chat input, dynamically display example questions based on the selected agent
st.markdown("### Example Questions")
selected_endpoint = st.session_state.selected_endpoint
if selected_endpoint == "Alpaca Trader":
    example_questions = [
        "What can you help me with?",
        "Back test trend following for TSLA last week",
        "Show me my account information",
        "Show me my current positions",
        "Place a market order to buy 1 share of INTL",
        "Place a limit order to buy 1 share of AAPL at $150"
    ]
elif selected_endpoint == "CEX Aggregator":
    example_questions = [
        "What exchanges are available?",
        "Show me my balance on Binance",
        "What is the price of BTC/USDC on Bybit?",
        "Show me arbitrage opportunities for BTC/USDC between Binance and Bybit",
        "Run a mean reversion backtest for BTC/USDT on Binance with a 1 week lookback and 1.5% threshold",
        "Run a trend following backtest for ETH/USDT on Bybit with 50-day MA and RSI(14) with overbought at 75 and oversold at 25"
    ]
elif selected_endpoint == "Polymarket Agent":
    example_questions = [
        "What can you help me with?",
        "What markets are available on Polymarket right now?",
        "Tell me about upcoming election markets",
        "Show me market with most volume and liquidity",
        "Show me the markets ending today"
    ]
else:
    example_questions = []

# Create 2 rows of 3 buttons each
col1, col2, col3 = st.columns(3)
for i, question in enumerate(example_questions):
    if i < 3:
        if col1.button(question, key=f"button_{question}"):
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
                        streaming=STREAMING_ENABLED
                    )
                    if response and "response" in response:
                        message_placeholder.markdown(response["response"])
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response["response"]}
                        )
                    else:
                        message_placeholder.markdown("❌ Error: Invalid response from server")
                except Exception as e:
                    message_placeholder.markdown(f"❌ Error: {str(e)}")
    elif i < 6:
        if col2.button(question, key=f"button_{question}"):
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
                        streaming=STREAMING_ENABLED
                    )
                    if response and "response" in response:
                        message_placeholder.markdown(response["response"])
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response["response"]}
                        )
                    else:
                        message_placeholder.markdown("❌ Error: Invalid response from server")
                except Exception as e:
                    message_placeholder.markdown(f"❌ Error: {str(e)}")
