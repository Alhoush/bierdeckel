from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.db import get_db
from models.session import TableSession
from models.menu import MenuItem

router = APIRouter()

class AutoOrderToggle(BaseModel):
    enabled: bool
    menu_item_id: Optional[str] = None

# Auto-Bestellung an/ausschalten
@router.put("/session/{session_id}/auto-order")
def toggle_auto_order(session_id: str, data: AutoOrderToggle, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    if data.enabled:
        if not data.menu_item_id:
            # Letztes bestelltes Getränk nehmen
            from models.order import Order, OrderItem
            last_order = db.query(Order).filter(
                Order.session_id == session_id
            ).order_by(Order.created_at.desc()).first()

            if last_order:
                last_item = db.query(OrderItem).filter(
                    OrderItem.order_id == last_order.id
                ).first()
                if last_item:
                    data.menu_item_id = last_item.menu_item_id

        if not data.menu_item_id:
            raise HTTPException(status_code=400, detail="Kein Getränk ausgewählt und keine vorherige Bestellung")

        menu_item = db.query(MenuItem).filter(MenuItem.id == data.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail="Getränk nicht gefunden")

        session.auto_order = True
        session.auto_order_item_id = data.menu_item_id
        db.commit()

        return {
            "message": f"Auto-Bestellung aktiviert: {menu_item.name}",
            "auto_order": True,
            "item_name": menu_item.name,
            "item_id": menu_item.id
        }
    else:
        session.auto_order = False
        session.auto_order_item_id = None
        db.commit()

        return {
            "message": "Auto-Bestellung deaktiviert",
            "auto_order": False
        }

# Auto-Bestellung Status abrufen
@router.get("/session/{session_id}/auto-order")
def get_auto_order(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    item_name = None
    if session.auto_order_item_id:
        item = db.query(MenuItem).filter(MenuItem.id == session.auto_order_item_id).first()
        item_name = item.name if item else None

    return {
        "auto_order": session.auto_order,
        "item_id": session.auto_order_item_id,
        "item_name": item_name
    }