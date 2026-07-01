from fastapi import FastAPI
from app.routes.chat_route import router as chat_router
from app.routes.chat_route import router as chat_router
from app.routes.auth_route import router as auth_router

app = FastAPI(title="AI Backend API")

app.include_router(auth_router)
app.include_router(chat_router)

@app.get("/")
def home():
    return {"message": "AI Backend API Running"}