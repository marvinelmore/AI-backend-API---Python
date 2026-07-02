import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.core.redis_client import redis_client
from app.services.ai_service import stream_chat
from collections import defaultdict
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])
chat_sessions = defaultdict(list)

@router.post("/stream")
async def chat_stream(
        request: ChatRequest,
        current_user=Depends(get_current_user)):

    session_id = request.session_id
    prompt = request.prompt
    username = current_user.username

    key = f"user:{username}:session:{session_id}"

    # load history from Redis
    history_raw = redis_client.get(key)

    if history_raw:
        history = json.loads(history_raw)
    else:
        history = []

    #history = chat_sessions[session_id]

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

        #chat_sessions[session_id] = history
        redis_client.set(key, json.dumps(history))

    return StreamingResponse(generate(), media_type="text/plain")