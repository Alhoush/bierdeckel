from sqlalchemy import Column, String, Float, Boolean, ForeignKey
from database.db import Base
import uuid

class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # "Getränke", "Speisen", etc.
    image_url = Column(String)
    is_available = Column(Boolean, default=True)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)