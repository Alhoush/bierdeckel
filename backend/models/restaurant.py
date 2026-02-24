from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from database.db import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    address = Column(String)
    logo_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)