from fastapi import FastAPI
from database.db import engine, Base

from models.restaurant import Restaurant
from models.user import User
from models.table import Table
from models.drink import DrinkGroup, Invitation
from models.session import TableSession
from models.menu import MenuItem
from models.order import Order, OrderItem
from models.payment import Payment
from models.game import Game

from routes.restaurant import router as restaurant_router
from routes.auth import router as auth_router
from routes.table import router as table_router
from routes.session import router as session_router
from routes.menu import router as menu_router
from routes.order import router as order_router
from routes.payment import router as payment_router
from routes.game import router as game_router
from routes.service import router as service_router
from routes.drink import router as drink_router
from routes.bierdeckel import router as bierdeckel_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bierdeckel API")

app.include_router(restaurant_router)
app.include_router(auth_router)
app.include_router(table_router)
app.include_router(session_router)
app.include_router(menu_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(game_router)
app.include_router(service_router)
app.include_router(drink_router)
app.include_router(bierdeckel_router)

@app.get("/")
def home():
    return {"message": "Willkommen bei Bierdeckel API!"}

@app.get("/health")
def health():
    return {"status": "ok"}