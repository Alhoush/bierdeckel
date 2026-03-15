from sqlalchemy import Column, String, Integer, Float, ForeignKey
import uuid
from database.db import Base

class CustomerStats(Base):
    __tablename__ = "customer_stats"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    games_played = Column(Integer, default=0)
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)
    total_spent = Column(Float, default=0)