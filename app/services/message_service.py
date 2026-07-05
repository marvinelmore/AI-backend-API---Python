from app.models.message import Message


class MessageService:

    def __init__(self, db):
        self.db = db

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