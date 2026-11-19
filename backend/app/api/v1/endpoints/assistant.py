from typing import List, Dict, Optional, Any
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.services.gemini_service import GeminiService

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None
    crop_context: Optional[str] = None
    crop: Optional[str] = None
    location: Optional[str] = None
    recent_disease_scan: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    response: str
    model: str
    provider: str
    status: str

@router.post("/chat", response_model=ChatResponse)
def chat_with_copilot(req: ChatRequest):
    """Chat with the AgroAI agronomic assistant powered by Gemini / expert fallback."""
    effective_crop = req.crop_context or req.crop
    if req.recent_disease_scan:
        effective_crop = f"{effective_crop or 'Crop'} (Recent diagnosis: {req.recent_disease_scan})"
    
    result = GeminiService.ask_copilot(
        prompt=req.message,
        chat_history=req.history,
        crop_context=effective_crop
    )
    return ChatResponse(
        reply=result["reply"],
        response=result["reply"],
        model=result["model"],
        provider=result["provider"],
        status=result["status"]
    )
