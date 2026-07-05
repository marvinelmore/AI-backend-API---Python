import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.core.redis_client import redis_client
from app.services.ai_service import stream_chat
from collections import defaultdict
from app.auth.dependencies import get_current_user
from app.core.logger import logger
from app.services.conversation_service import ConversationService
from sqlalchemy.orm import Session
from app.database.dependencies import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])
chat_sessions = defaultdict(list)

@router.post("/stream/{conversation_id}")
async def chat_stream(
    conversation_id: int,
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)

):

    service = ConversationService(db)
    response = service.stream_response(
        username=current_user.username,
        conversation_id=conversation_id,
        prompt=request.prompt
    )

    if response is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"

        )
    return response
