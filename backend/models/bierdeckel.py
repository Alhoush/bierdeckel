from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
import uuid
from database.db import Base

class Bierdeckel(Base):
    __tablename__ = "bierdeckel"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    table_id = Column(String, ForeignKey("tables.id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    weight = Column(Float, default=0)  # Gewicht in Gramm
    status = Column(String, default="empty")  # empty, low, half, full
    last_updated = Column(DateTime, default=datetime.utcnow)