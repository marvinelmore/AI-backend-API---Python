import json

from fastapi.responses import StreamingResponse

from app.core.logger import logger
from app.core.redis_client import redis_client
from app.services.ai_service import stream_chat
from sqlalchemy.orm import Session

def stream_conversation_response(
    db: Session,
    username: str,
    session_id: str,
    prompt: str
):
    key = f"user:{username}:session:{session_id}"

    logger.info(
        f"User '{username}' started session '{session_id}'."
    )

    history_raw = redis_client.get(key)

    logger.info(
        f"Loaded Redis history for '{username}:{session_id}'."
    )

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

        logger.info(
            f"OpenAI response completed for '{username}'."
        )

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