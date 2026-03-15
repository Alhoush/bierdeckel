from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from datetime import datetime
import uuid
from database.db import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    game_type = Column(String, default="drink_race")
    status = Column(String, default="waiting")  # waiting, active, finished
    loser_session_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class GamePlayer(Base):
    __tablename__ = "game_players"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    status = Column(String, default="pending")  # pending, approved, declined
    finished = Column(Boolean, default=False)
    finished_at = Column(DateTime, nullable=True)