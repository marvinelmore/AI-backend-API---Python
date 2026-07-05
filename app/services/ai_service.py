import os
from openai import OpenAI
from dotenv import load_dotenv
from app.core.config import settings

load_dotenv()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def chat_with_ai(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"OpenAI error: {e}")
        return "AI service is temporarily unavailable."

def stream_chat(messages: list):

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content

def generate_conversation_title(prompt: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Generate a short conversation title. Use 3 to 6 words. No quotes. No punctuation at the end."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content.strip()