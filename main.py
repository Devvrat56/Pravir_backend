from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from chatbot import Chatbot
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Prarvi AI  API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chatbot
# Note: In production, you might want to use a singleton or dependency injection
chatbot = Chatbot("knowledge_base.json")

class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    context: List[dict]

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not chatbot.client and not request.api_key:
        raise HTTPException(status_code=400, detail="Groq API Key not configured")
    
    # Update API key if provided
    if request.api_key:
        from groq import Groq
        chatbot.client = Groq(api_key=request.api_key)

    try:
        response_text, context = chatbot.process_query(request.message)
        return ChatResponse(response=response_text, context=context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model": "llama-3.3-70b-versatile"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
