from sqlalchemy import Column, String, Float, DateTime, Integer, ForeignKey
from datetime import datetime
import uuid
from database.db import Base

class Bierdeckel(Base):
    __tablename__ = "bierdeckel"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    label = Column(String, nullable=False)
    table_id = Column(String, ForeignKey("tables.id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    qr_code = Column(String)
    weight = Column(Float, default=0)
    status = Column(String, default="empty")
    last_updated = Column(DateTime, default=datetime.utcnow)