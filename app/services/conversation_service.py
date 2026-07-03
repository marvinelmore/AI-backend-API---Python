import json

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.logger import logger
from app.core.redis_client import redis_client
from app.models.user import User
from app.services.ai_service import stream_chat
from app.models.conversation import Conversation
from app.models.message import Message

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

        def generate():
            full_response = ""

            for chunk in stream_chat(history):
                full_response += chunk
                yield chunk

            history.append({
                "role": "assistant",
                "content": full_response
            })

            redis_client.set(key, json.dumps(history))

            logger.info(
                f"Saved Redis history for '{username}:{session_id}'."
            )

        return StreamingResponse(
            generate(),
            media_type="text/plain"
        )