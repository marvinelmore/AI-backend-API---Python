from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
#from app.services.ai_service import generate_response, summarize_text
from app.services.ai_service import chat_with_ai

router = APIRouter(prefix="/chat", tags=["Chat"])

# simple in-memory store (for now)
chat_history = []

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    global chat_history

    # add user message
    chat_history.append({
        "role": "user",
        "content": request.prompt
    })

    response = await chat_with_ai(request.prompt)

    # add assistant response
    chat_history.append({
        "role": "assistant",
        "content": response
    })

    return ChatResponse(
        response=response
    )

# @router.post("/chat")
# async def chat(prompt: str):
#     return await generate_response(prompt)
#
# @router.post("/summarize")
# async def summarize(text: str):
#     return await summarize_text(text)