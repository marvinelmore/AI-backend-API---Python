from pydantic import BaseModel

class CurrentUser(BaseModel):
    username: str