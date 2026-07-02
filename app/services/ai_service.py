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

# async def generate_response(prompt: str):
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "user", "content": prompt}
#         ]
#     )
#
#     return {"result": response.choices[0].message.content}
#
#
# async def summarize_text(text: str):
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "user", "content": f"Summarize this:\n{text}"}
#         ]
#     )
#
#     return {"summary": response.choices[0].message.content}