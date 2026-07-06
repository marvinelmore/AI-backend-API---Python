import json
from uuid import uuid4
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.redis_client import redis_client
from app.models.user import User
from app.services.ai_service import (
    stream_chat,
    generate_conversation_title
)
from app.models.conversation import Conversation
from app.models.message import Message
from sqlalchemy import and_
from app.services.title_service import TitleService
from app.services.cache_service import CacheService
from app.services.message_service import MessageService
from app.services.conversation_repository import ConversationRepository
from app.services.user_service import UserService

class ConversationService:

    def __init__(self, db: Session):
        self.db = db
        self.title_service = TitleService()
        self.cache_service = CacheService()
        self.message_service = MessageService(db)
        self.conversation_repository = ConversationRepository(db)
        self.user_service = UserService(db)

    def get_or_create_user(self, username: str):
        user = self.db.query(User).filter(
            User.username == username
        ).first()

        if user:
            return user

        user = User(
            username=username,
            password_hash="oauth_or_jwt_user"
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"Created new user record for '{username}'.")

        return user

    def stream_response(
        self,
        username: str,
        conversation_id: int,
        prompt: str
    ):

        conversation = self.get_conversation_by_id(
            username=username,
            conversation_id=conversation_id
        )

        user = self.user_service.get_or_create_user(username)

        conversation = self.conversation_repository.get_by_id_for_user(
            conversation_id=conversation_id,
            user_id=user.id
        )

        if not conversation:
            return None

        conversation = self.generate_title_if_needed(
            conversation=conversation,
            prompt=prompt
        )

        session_id = conversation.session_id
        key = f"user:{username}:session:{session_id}"

        logger.info(
            f"User '{user.username}' started session '{session_id}'."
        )

        history = self.cache_service.get_history(key)

        history.append({
            "role": "user",
            "content": prompt
        })

        self.message_service.save_message(
            conversation_id=conversation.id,
            role="user",
            content=prompt
        )

        def generate():
            full_response = ""

            for chunk in stream_chat(history):
                full_response += chunk
                yield chunk

            history.append({
                "role": "assistant",
                "content": full_response
            })

            self.message_service.save_message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response
            )

            self.cache_service.save_history(key, history)

            logger.info(
                f"Saved Redis history for '{username}:{session_id}'."
            )

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )

    def get_or_create_conversation(
            self,
            user_id: int,
            session_id: str,
            prompt: str
    ):
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.session_id == session_id
            )
        ).first()

        if conversation:
            return conversation

        title = self.title_service.generate_title(prompt)

        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            title=title
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def create_conversation(
            self,
            username: str,
            title: str = "New Conversation"
    ):
        user = self.user_service.get_or_create_user(username)

        conversation = Conversation(
            user_id=user.id,
            session_id=str(uuid4()),
            title=title
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def save_message(
            self,
            conversation_id: int,
            role: str,
            content: str
    ):
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        return message

    def get_user_conversations(
            self,
            username: str,
            page: int = 1,
            page_size: int = 20
    ):
        user = self.user_service.get_or_create_user(username)

        return self.conversation_repository.get_all_for_user(
            user_id=user.id,
            page=page,
            page_size=page_size
        )

    def get_conversation_messages(
            self,
            username: str,
            conversation_id: int
    ):
        user = self.user_service.get_or_create_user(username)

        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )
        ).first()

        if not conversation:
            return None

        return self.db.query(Message).filter(
            and_(
                Message.conversation_id == conversation.id
            )
        ).order_by(
            Message.created_at.asc()
        ).all()

    def delete_conversation(
            self,
            username: str,
            conversation_id: int
    ):
        user = self.user_service.get_or_create_user(username)
        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )).first()

        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()

        return True

    def get_conversation_by_id(
            self,
            username: str,
            conversation_id: int
    ):
        user = self.user_service.get_or_create_user(username)

        return self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )).first()

    def rename_conversation(
            self,
            username: str,
            conversation_id: int,
            title: str
    ):
        user = self.user_service.get_or_create_user(username)

        conversation = self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user.id
            )).first()

        if not conversation:
            return None

        conversation.title = title

        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def generate_title_if_needed(
            self,
            conversation,
            prompt: str
    ):
        if conversation.title != "New Conversation":
            return conversation

        title = self.title_service.generate_title(prompt)

        return self.conversation_repository.update_title(
            conversation=conversation,
            title=title
        )

    def search_conversations(
            self,
            username: str,
            search: str
    ):
        user = self.user_service.get_or_create_user(username)

        return self.conversation_repository.search_for_user(
            user_id=user.id,
            search=search
        )