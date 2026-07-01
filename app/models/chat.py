from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    session_id: str
    prompt: str

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatResponse(BaseModel):
    response: str