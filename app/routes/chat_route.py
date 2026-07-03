import json

from fastapi import APIRouter, Depends
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

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)

):

    conversation_service = ConversationService(db)
    return conversation_service.stream_response(
        username=current_user.username,
        session_id=request.session_id,
        prompt=request.prompt
    )
