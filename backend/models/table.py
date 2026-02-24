from sqlalchemy import Column, String, Integer, ForeignKey
from database.db import Base
import uuid

class Table(Base):
    __tablename__ = "tables"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    table_number = Column(Integer, nullable=False)
    qr_code = Column(String)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)