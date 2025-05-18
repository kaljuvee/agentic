from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from agent.polymarket_agent import create_agent
from agents import Runner
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class Role(str, Enum):
    AGENT = "agent"
    USER = "user"

class Message(BaseModel):
    role: Role
    content: str

class ChatRequest(BaseModel):
    input: str = Field(..., min_length=1, max_length=500)
    history: List[Message] = Field(default_factory=list)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('input')
    @classmethod
    def validate_input(cls, v):
        # Remove any potentially harmful characters
        v = ''.join(c for c in v if c.isprintable())
        return v.strip()

@app.post("/chat")
async def chat_stream(request: ChatRequest):
    async def stream():
        try:
            # Create a new agent instance
            agent = create_agent()
            
            # Apply any configuration from the request
            if request.config:
                agent.update_config(request.config)
            
            # Run the agent using Runner.run
            response = await Runner.run(agent, input=request.input)
            
            # Stream the response
            if hasattr(response, 'final_output'):
                yield f"data: {response.final_output}\n\n"
            else:
                yield f"data: {str(response)}\n\n"
                
        except Exception as e:
            yield f"data: Error encountered: {str(e)}\n\n"
            
    return StreamingResponse(stream(), media_type="text/event-stream")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}