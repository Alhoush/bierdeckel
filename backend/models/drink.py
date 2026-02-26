from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime
import uuid
from database.db import Base

class DrinkGroup(Base):
    __tablename__ = "drink_groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    invite_code = Column(String, unique=True, nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    from_session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    to_session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    group_id = Column(String, ForeignKey("drink_groups.id"), nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)