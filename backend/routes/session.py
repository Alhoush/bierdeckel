from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.session import TableSession
from models.table import Table

router = APIRouter()

# Session erstellen (Gast scannt QR-Code)
@router.post("/r/{restaurant_id}/table/{table_number}/scan")
def scan_qr(restaurant_id: str, table_number: int, db: Session = Depends(get_db)):
    # Tisch finden
    table = db.query(Table).filter(
        Table.restaurant_id == restaurant_id,
        Table.table_number == table_number
    ).first()
    if not table:
        raise HTTPException(status_code=404, detail="Tisch nicht gefunden")

    # Neue Session erstellen
    new_session = TableSession(
        table_id=table.id,
        restaurant_id=restaurant_id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "session_id": new_session.id,
        "table_number": table_number,
        "restaurant_id": restaurant_id,
        "is_active": new_session.is_active,
        "created_at": str(new_session.created_at)
    }

# Session abrufen
@router.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    return {
        "session_id": session.id,
        "table_id": session.table_id,
        "restaurant_id": session.restaurant_id,
        "is_active": session.is_active,
        "created_at": str(session.created_at)
    }

# Session beenden (Gast geht)
@router.put("/session/{session_id}/close")
def close_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    
    session.is_active = False
    db.commit()
    return {"message": "Session beendet", "session_id": session_id}

# Alle aktiven Sessions eines Restaurants (für Service-Dashboard)
@router.get("/restaurant/{restaurant_id}/sessions")
def get_active_sessions(restaurant_id: str, db: Session = Depends(get_db)):
    sessions = db.query(TableSession).filter(
        TableSession.restaurant_id == restaurant_id,
        TableSession.is_active == True
    ).all()
    
    result = []
    for s in sessions:
        table = db.query(Table).filter(Table.id == s.table_id).first()
        result.append({
            "session_id": s.id,
            "table_number": table.table_number if table else None,
            "is_active": s.is_active,
            "created_at": str(s.created_at)
        })
    return result