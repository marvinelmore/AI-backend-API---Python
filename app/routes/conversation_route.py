from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.database.dependencies import get_db
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


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