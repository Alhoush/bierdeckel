from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from database.db import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    avatar_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)