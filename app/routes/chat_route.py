from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.services.ai_service import stream_chat
from collections import defaultdict

router = APIRouter(prefix="/chat", tags=["Chat"])

chat_sessions = defaultdict(list)


@router.post("/stream")
async def chat_stream(request: ChatRequest):

    session_id = request.session_id
    prompt = request.prompt

    history = chat_sessions[session_id]

    history.append({
        "role": "user",
        "content": prompt
    })

    def generate():
        full_response = ""

        for chunk in stream_chat(history):
            full_response += chunk
            yield chunk

        history.append({
            "role": "assistant",
            "content": full_response
        })

        chat_sessions[session_id] = history

    return StreamingResponse(generate(), media_type="text/plain")