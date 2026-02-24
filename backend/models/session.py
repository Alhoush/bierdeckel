from sqlalchemy import Column, String, DateTime, Boolean
from datetime import datetime
import uuid
from database.db import Base

class TableSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    table_number = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)