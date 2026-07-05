from app.services.ai_service import generate_conversation_title


class TitleService:

    def generate_title(self, prompt: str) -> str:
        title = generate_conversation_title(prompt).strip()

        if len(title) > 60:
            title = title[:60]

        return title