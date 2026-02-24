from sqlalchemy import Column, String, ForeignKey
from database.db import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="staff")  # "owner", "admin", "staff"
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)