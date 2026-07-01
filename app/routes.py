from fastapi import APIRouter
from app.services import generate_response, summarize_text

router = APIRouter()

@router.post("/chat")
async def chat(prompt: str):
    return await generate_response(prompt)

@router.post("/summarize")
async def summarize(text: str):
    return await summarize_text(text)