from fastapi import FastAPI
from database.db import engine, Base

# Alle Models importieren damit Tabellen erstellt werden
from models.restaurant import Restaurant
from models.user import User
from models.table import Table
from models.session import TableSession
from models.menu import MenuItem
from models.order import Order, OrderItem
from models.payment import Payment
from models.game import Game

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bierdeckel API")

@app.get("/")
def home():
    return {"message": "Willkommen bei Bierdeckel API!"}

@app.get("/health")
def health():
    return {"status": "ok"}