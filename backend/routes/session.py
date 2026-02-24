from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.db import get_db
from models.session import TableSession

router = APIRouter()

# Session erstellen (wenn QR-Code gescannt wird)
@router.post("/session/{table_number}")
def create_session(table_number: str, db: Session = Depends(get_db)):
    new_session = TableSession(table_number=table_number)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return {
        "session_id": new_session.id,
        "table_number": new_session.table_number,
        "is_active": new_session.is_active,
        "created_at": str(new_session.created_at)
    }

# Session abrufen
@router.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        return {"error": "Session nicht gefunden"}
    return {
        "session_id": session.id,
        "table_number": session.table_number,
        "is_active": session.is_active,
        "created_at": str(session.created_at)
    }