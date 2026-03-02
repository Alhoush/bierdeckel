from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.session import TableSession
from models.bierdeckel import Bierdeckel
from models.table import Table

router = APIRouter()

# Session erstellen (Gast scannt Bierdeckel QR-Code)
@router.post("/r/{restaurant_id}/bd/{bierdeckel_id}/scan")
def scan_bierdeckel(restaurant_id: str, bierdeckel_id: str, db: Session = Depends(get_db)):
    bd = db.query(Bierdeckel).filter(
        Bierdeckel.id == bierdeckel_id,
        Bierdeckel.restaurant_id == restaurant_id
    ).first()
    if not bd:
        raise HTTPException(status_code=404, detail="Bierdeckel nicht gefunden")

    table = db.query(Table).filter(Table.id == bd.table_id).first()

    # Prüfen ob schon eine aktive Session auf diesem Bierdeckel existiert
    existing = db.query(TableSession).filter(
        TableSession.bierdeckel_id == bierdeckel_id,
        TableSession.is_active == True
    ).first()
    if existing:
        return {
            "session_id": existing.id,
            "bierdeckel_id": bierdeckel_id,
            "table_number": table.table_number if table else None,
            "restaurant_id": restaurant_id,
            "is_active": existing.is_active,
            "message": "Bestehende Session"
        }

    new_session = TableSession(
        bierdeckel_id=bierdeckel_id,
        table_id=bd.table_id,
        restaurant_id=restaurant_id
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "session_id": new_session.id,
        "bierdeckel_id": bierdeckel_id,
        "table_number": table.table_number if table else None,
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
    
    table = db.query(Table).filter(Table.id == session.table_id).first()
    
    return {
        "session_id": session.id,
        "bierdeckel_id": session.bierdeckel_id,
        "table_number": table.table_number if table else None,
        "restaurant_id": session.restaurant_id,
        "is_active": session.is_active,
        "group_id": session.group_id,
        "created_at": str(session.created_at)
    }

# Session beenden
@router.put("/session/{session_id}/close")
def close_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    session.is_active = False
    db.commit()
    return {"message": "Session beendet", "session_id": session_id}

# Alle aktiven Sessions eines Restaurants
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
            "bierdeckel_id": s.bierdeckel_id,
            "table_number": table.table_number if table else None,
            "is_active": s.is_active,
            "created_at": str(s.created_at)
        })
    return result