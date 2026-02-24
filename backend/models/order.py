from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from datetime import datetime
import uuid
from database.db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    status = Column(String, default="pending")  # pending, preparing, delivered
    total = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(String, ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, nullable=False)