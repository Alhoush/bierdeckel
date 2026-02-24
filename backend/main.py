from fastapi import FastAPI
from database.db import engine, Base

# Datenbank-Tabellen erstellen
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bierdeckel API")

@app.get("/")
def home():
    return {"message": "Willkommen bei Bierdeckel API!"}

@app.get("/health")
def health():
    return {"status": "ok"}