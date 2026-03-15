from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime
from datetime import datetime
import uuid
from database.db import Base

class LoyaltyProgram(Base):
    __tablename__ = "loyalty_programs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False)
    required_orders = Column(Integer, default=10)
    reward_type = Column(String, default="free_drink")  # free_drink, discount
    discount_percent = Column(Float, nullable=True)
    menu_item_id = Column(String, ForeignKey("menu_items.id"), nullable=True)  # null = alle Getränke
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerLoyalty(Base):
    __tablename__ = "customer_loyalty"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    loyalty_program_id = Column(String, ForeignKey("loyalty_programs.id"), nullable=False)
    current_count = Column(Integer, default=0)
    rewards_claimed = Column(Integer, default=0)