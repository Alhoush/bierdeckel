from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite Datenbank (erstellt eine Datei "bierdeckel.db")
DATABASE_URL = "sqlite:///bierdeckel.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Datenbank-Session für API-Routen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()