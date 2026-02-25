from fastapi import FastAPI
from database.db import engine, Base

from models.restaurant import Restaurant
from models.user import User
from models.table import Table
from models.session import TableSession
from models.menu import MenuItem
from models.order import Order, OrderItem
from models.payment import Payment
from models.game import Game

from routes.restaurant import router as restaurant_router
from routes.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bierdeckel API")

app.include_router(restaurant_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Willkommen bei Bierdeckel API!"}

@app.get("/health")
def health():
    return {"status": "ok"}