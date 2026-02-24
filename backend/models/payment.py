from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from datetime import datetime
import uuid
from database.db import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_type = Column(String, default="single")  # "single" oder "group"
    status = Column(String, default="pending")  # pending, completed
    created_at = Column(DateTime, default=datetime.utcnow)