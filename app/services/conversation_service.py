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


class ConversationService:

    def __init__(self, db: Session):
        self.db = db

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

        if not conversation:
            return None

        session_id = conversation.session_id
        key = f"user:{username}:session:{session_id}"
        user = self.get_or_create_user(username)

        conversation = self.get_or_create_conversation(
            user_id=user.id,
            session_id=session_id,
            prompt=prompt
        )

        logger.info(
            f"User '{user.username}' started session '{session_id}'."
        )

        history_raw = redis_client.get(key)

        if history_raw:
            history = json.loads(history_raw)
        else:
            history = []

        history.append({
            "role": "user",
            "content": prompt
        })

        self.save_message(
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

            self.save_message(
                conversation_id=conversation.id,
                role="assistant",
                content=full_response
            )

            redis_client.set(key, json.dumps(history))

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

        title = generate_conversation_title(prompt)

        if len(title) > 60:
            title = title[:60]

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
        user = self.get_or_create_user(username)

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

    def get_user_conversations(self, username: str):
        user = self.get_or_create_user(username)
        return self.db.query(Conversation).filter(
         and_(
          Conversation.user_id == user.id
         )).order_by(
            Conversation.created_at.desc()
         ).all()

    def get_conversation_messages(
            self,
            username: str,
            conversation_id: int
    ):
        user = self.get_or_create_user(username)

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
        user = self.get_or_create_user(username)
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
        user = self.get_or_create_user(username)

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
        user = self.get_or_create_user(username)

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