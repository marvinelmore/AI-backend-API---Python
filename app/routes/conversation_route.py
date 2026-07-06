from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.services.conversation_service import ConversationService
from app.models.conversation_request import UpdateConversationRequest

router = APIRouter(prefix="/conversations", tags=["Conversations"])


class CreateConversationRequest(BaseModel):
    title: str = "New Conversation"


@router.post("")
async def create_conversation(
    request: CreateConversationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)

    conversation = service.create_conversation(
        username=current_user.username,
        title=request.title
    )

    return conversation


@router.get("")
async def get_conversations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)

    conversations = service.get_user_conversations(
        current_user.username
    )

    return conversations


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)

    messages = service.get_conversation_messages(
        username=current_user.username,
        conversation_id=conversation_id
    )

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return messages


@router.patch("/{conversation_id}")
async def rename_conversation(
    conversation_id: int,
    request: UpdateConversationRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)

    conversation = service.rename_conversation(
        username=current_user.username,
        conversation_id=conversation_id,
        title=request.title
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)

    deleted = service.delete_conversation(
        username=current_user.username,
        conversation_id=conversation_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return {
        "success": True,
        "message": "Conversation deleted successfully"
    }


@router.get("/search")
async def search_conversations(
    q: str = Query(...),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = ConversationService(db)

    return service.search_conversations(
        username=current_user.username,
        search=q
    )