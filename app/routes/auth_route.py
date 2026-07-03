from fastapi import APIRouter
from pydantic import BaseModel

from app.auth.auth_service import login_user
from app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str


@router.post("/login")
async def login(request: LoginRequest):

    token = login_user(request.username)
    logger.info(f"User '{request.username}' logged in successfully.")

    return {
        "access_token": token,
        "token_type": "bearer"
    }