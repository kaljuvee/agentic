from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph.travel_agent import stream_response
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Make this more restrictive
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Authorization"],
)


class Message(BaseModel):
    input: str
    userId: str
    messageHistory: list[dict]


@app.post("/chat")
async def generate_travel_stream(message: Message):
    """
    Generate a streaming response for travel queries.
    
    Args:
        message (Message): The message containing the user's query
        
    Returns:
        StreamingResponse: A streaming response containing the agent's response
    """
    return StreamingResponse(
        stream_response(message.input, message.userId), 
        media_type="text/event-stream"
    )
