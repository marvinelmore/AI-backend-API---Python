from uuid import uuid4
from sqlalchemy import and_
from app.models.conversation import Conversation


class ConversationRepository:

    def __init__(self, db):
        self.db = db

    def create_conversation(
        self,
        user_id: int,
        title: str = "New Conversation"
    ):
        conversation = Conversation(
            user_id=user_id,
            session_id=str(uuid4()),
            title=title
        )

        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def get_by_id_for_user(
        self,
        conversation_id: int,
        user_id: int
    ):
        return self.db.query(Conversation).filter(
            and_(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        ).first()

    def get_by_session_for_user(
        self,
        user_id: int,
        session_id: str
    ):
        return self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id,
                Conversation.session_id == session_id
            )
        ).first()

    def get_all_for_user(self, user_id: int):
        return self.db.query(Conversation).filter(
            and_(
                Conversation.user_id == user_id
            )
        ).order_by(
            Conversation.created_at.desc()
        ).all()

    def rename_for_user(
            self,
            conversation_id: int,
            user_id: int,
            title: str
    ):
        conversation = self.get_by_id_for_user(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation:
            return None

        conversation.title = title

        self.db.commit()
        self.db.refresh(conversation)

        return conversation

    def delete_for_user(
            self,
            conversation_id: int,
            user_id: int
    ):
        conversation = self.get_by_id_for_user(
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation:
            return False

        self.db.delete(conversation)
        self.db.commit()

        return True

    def update_title(
            self,
            conversation,
            title: str
    ):
        conversation.title = title

        self.db.commit()
        self.db.refresh(conversation)

        return conversation