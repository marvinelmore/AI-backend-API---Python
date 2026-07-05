import json

from app.core.redis_client import redis_client


class CacheService:

    def get_history(self, key: str):
        history_raw = redis_client.get(key)

        if history_raw:
            return json.loads(history_raw)

        return []

    def save_history(self, key: str, history: list):
        redis_client.set(
            key,
            json.dumps(history)
        )