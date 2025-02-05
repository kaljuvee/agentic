from pydantic_ai import Agent, RunContext
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class ChatMessage(BaseModel):
    """Structure for chat messages"""
    content: str
    timestamp: datetime = datetime.now()
    sentiment: Optional[str] = None
    role: str = "assistant"

class ChatHistory(BaseModel):
    """Structure for maintaining chat history"""
    messages: List[ChatMessage] = []

# Create an agent with a friendly personality
chat_agent = Agent(
    os.getenv('MODEL_NAME'),  # Load model name from environment variables
    result_type=ChatMessage,
    system_prompt="""
    You are a friendly and helpful AI assistant. Your responses should be:
    - Conversational and engaging
    - Helpful and informative 
    - Concise but thorough
    - Always polite and professional
    
    Analyze the sentiment of each message and include it in your response.
    Keep your responses focused and relevant to the user's questions.
    """
)

@chat_agent.tool
def analyze_sentiment(ctx: RunContext, message: str) -> str:
    """Analyze the sentiment of a message"""
    # Simple sentiment analysis
    positive_words = {'happy', 'great', 'good', 'love', 'excellent', 'awesome', 'wonderful'}
    negative_words = {'sad', 'bad', 'hate', 'terrible', 'awful', 'poor'}
    
    words = set(message.lower().split())
    if words & positive_words:
        return 'positive'
    elif words & negative_words:
        return 'negative'
    return 'neutral'

def chat():
    print("Welcome to PydanticAI Chat! (Type 'exit' to end the conversation)")
    print("-" * 50)
    
    chat_history = ChatHistory()
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'exit':
            print("\nGoodbye! Thanks for chatting!")
            break
            
        try:
            # Get sentiment through the agent
            sentiment_result = chat_agent.run_sync(
                "analyze_sentiment",
                inputs={"message": user_input}
            )
            
            # Create user message with explicit role
            user_message = ChatMessage(
                content=user_input, 
                role="user", 
                sentiment=sentiment_result.data
            )
            chat_history.messages.append(user_message)
            
            # Get AI response
            result = chat_agent.run_sync(
                user_input,
                context={"history": chat_history.messages}
            )
            
            # Add response to history
            chat_history.messages.append(result.data)
            
            # Print the response
            print(f"\nAssistant: {result.data.content}")
            print(f"Sentiment: {result.data.sentiment}")
            
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    chat()
