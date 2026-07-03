import json

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.redis_client import redis_client
from app.models.user import User
from app.services.ai_service import stream_chat
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
        session_id: str,
        prompt: str
    ):
        key = f"user:{username}:session:{session_id}"
        user = self.get_or_create_user(username)

        conversation = self.get_or_create_conversation(
            user_id=user.id,
            session_id=session_id
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
            session_id: str
    ):
        conversation = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.title == session_id
        ).first()

        if conversation:
            return conversation

        conversation = Conversation(
            user_id=user_id,
            title=session_id
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