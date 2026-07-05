from pydantic import BaseModel


class UpdateConversationRequest(BaseModel):
    title: str

