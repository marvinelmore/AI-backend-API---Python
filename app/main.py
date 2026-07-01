from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="AI Backend API")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "AI Backend API Running"}