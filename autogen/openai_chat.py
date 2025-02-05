import os
from autogen import AssistantAgent, UserProxyAgent

# Configure the LLM
llm_config = {
    "config_list": [{
        "model": "gpt-4",
        "api_key": os.environ.get("OPENAI_API_KEY")
    }]
}

# Create an assistant agent
assistant = AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message="You are a helpful AI assistant with expertise in programming and problem solving."
)

# Create a user proxy agent
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding", "use_docker": False}
)

# Start the chat with a coding task
user_proxy.initiate_chat(
    assistant,
    message="Write a Python function that calculates the Fibonacci sequence up to n terms and create a simple plot to visualize it."
)
