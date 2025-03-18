from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph.cex_aggregator import stream_response, get_response
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

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
    role: str
    content: str

class ChatRequest(BaseModel):
    input: str
    history: Optional[List[Message]] = []
    config: Optional[Dict[str, Any]] = {}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that follows the standardized schema.
    
    Args:
        request (ChatRequest): The chat request containing input, history, and config
        
    Returns:
        StreamingResponse or JSONResponse: A streaming or JSON response from the agent
    """
    # Extract parameters
    input_message = request.input
    history = request.history
    config = request.config
    
    if not input_message:
        return JSONResponse(
            status_code=400, 
            content={"error": "Missing required parameter: 'input'"}
        )
    
    try:
        # Extract the last user message from history if available
        context = ""
        for msg in reversed(history):
            if msg.role == "user":
                context = msg.content
                break
                
        # Combine context with current input if helpful
        query = input_message
        if context:
            query = f"Context: {context}\nCurrent question: {input_message}"
            
        # Generate a thread_id from config if provided
        thread_id = config.get("thread_id", "cex_demo")
        
        # Determine if streaming is requested (default to True)
        use_streaming = config.get("streaming", True)
        
        if use_streaming:
            return StreamingResponse(
                stream_response(query, thread_id), 
                media_type="text/event-stream"
            )
        else:
            # For non-streaming requests, use get_response and return JSON
            response = get_response(query, thread_id)
            if response and "messages" in response:
                last_message = response["messages"][-1].content
                return JSONResponse(content={"response": last_message})
            else:
                return JSONResponse(
                    status_code=500,
                    content={"error": "Invalid response from agent"}
                )
                
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )
