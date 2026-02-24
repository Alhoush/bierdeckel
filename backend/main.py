from fastapi import FastAPI
from database.db import engine, Base
from routes.session import router as session_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bierdeckel API")

# Routes einbinden
app.include_router(session_router)

@app.get("/")
def home():
    return {"message": "Willkommen bei Bierdeckel API!"}

@app.get("/health")
def health():
    return {"status": "ok"}