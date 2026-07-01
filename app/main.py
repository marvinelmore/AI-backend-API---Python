from fastapi import FastAPI
from app.routes.chat_route import router as chat_router

app = FastAPI(title="AI Backend API")

app.include_router(chat_router)

@app.get("/")
def home():
    return {"message": "AI Backend API Running"}