from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database.db import get_db
from models.bierdeckel import Bierdeckel
from models.table import Table
import qrcode
import io
import os
import base64

router = APIRouter()

class BierdeckelCreate(BaseModel):
    label: str

class WeightUpdate(BaseModel):
    bierdeckel_id: str
    weight: float

def weight_to_status(weight: float) -> str:
    if weight < 100:
        return "no_glass"
    elif weight < 300:
        return "empty"
#   elif weight < 320:
#      return "half"
    else:
        return "full"

# Bierdeckel erstellen (Admin)
@router.post("/table/{table_id}/bierdeckel")
def create_bierdeckel(table_id: str, data: BierdeckelCreate, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Tisch nicht gefunden")

    new_bd = Bierdeckel(
        label=data.label,
        table_id=table_id,
        restaurant_id=table.restaurant_id
    )
    db.add(new_bd)
    db.commit()
    db.refresh(new_bd)

    # QR-Code URL generieren
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    qr_url = f"{frontend_url}/r/{table.restaurant_id}/bd/{new_bd.id}"
    new_bd.qr_code = qr_url
    db.commit()

    return {
        "id": new_bd.id,
        "label": new_bd.label,
        "table_number": table.table_number,
        "qr_code_url": new_bd.qr_code
    }

# Alle Bierdeckel eines Tisches
@router.get("/table/{table_id}/bierdeckel")
def get_bierdeckel_by_table(table_id: str, db: Session = Depends(get_db)):
    bierdeckel = db.query(Bierdeckel).filter(Bierdeckel.table_id == table_id).all()
    table = db.query(Table).filter(Table.id == table_id).first()

    return [
        {
            "id": bd.id,
            "label": bd.label,
            "table_number": table.table_number if table else None,
            "qr_code_url": bd.qr_code,
            "weight": bd.weight,
            "status": bd.status
        }
        for bd in bierdeckel
    ]

# QR-Code als Bild
@router.get("/bierdeckel/{bierdeckel_id}/qr")
def get_qr_code(bierdeckel_id: str, db: Session = Depends(get_db)):
    bd = db.query(Bierdeckel).filter(Bierdeckel.id == bierdeckel_id).first()
    if not bd:
        raise HTTPException(status_code=404, detail="Bierdeckel nicht gefunden")

    table = db.query(Table).filter(Table.id == bd.table_id).first()

    qr = qrcode.make(bd.qr_code)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "bierdeckel_id": bd.id,
        "label": bd.label,
        "table_number": table.table_number if table else None,
        "qr_code_url": bd.qr_code,
        "qr_code_image": f"data:image/png;base64,{qr_base64}"
    }

# Gewicht aktualisieren (MQTT Bridge)
@router.post("/bierdeckel/update")
def update_weight(data: WeightUpdate, db: Session = Depends(get_db)):
    bd = db.query(Bierdeckel).filter(Bierdeckel.id == data.bierdeckel_id).first()
    if not bd:
        raise HTTPException(status_code=404, detail="Bierdeckel nicht gefunden")

    bd.weight = data.weight
    bd.status = weight_to_status(data.weight)
    bd.last_updated = datetime.utcnow()
    db.commit()

    # Auto-Bestellung prüfen
    auto_ordered = False
    if bd.status == "empty":
        from models.session import TableSession
        from models.order import Order, OrderItem
        from models.menu import MenuItem

        active_session = db.query(TableSession).filter(
            TableSession.bierdeckel_id == bd.id,
            TableSession.is_active == True,
            TableSession.auto_order == True
        ).first()

        if active_session and active_session.auto_order_item_id:
            menu_item = db.query(MenuItem).filter(
                MenuItem.id == active_session.auto_order_item_id
            ).first()

            if menu_item:
                # Prüfen ob nicht schon eine offene Auto-Bestellung existiert
                existing = db.query(Order).filter(
                    Order.session_id == active_session.id,
                    Order.source == "auto_order",
                    Order.status.in_(["pending", "preparing"])
                ).first()

                if not existing:
                    new_order = Order(
                        session_id=active_session.id,
                        total=menu_item.price,
                        status="pending",
                        source="auto_order"
                    )
                    db.add(new_order)
                    db.flush()

                    new_item = OrderItem(
                        order_id=new_order.id,
                        menu_item_id=menu_item.id,
                        quantity=1,
                        price=menu_item.price
                    )
                    db.add(new_item)
                    db.commit()
                    auto_ordered = True
                    print(f"Auto-Bestellung: {menu_item.name} für Session {active_session.id}")

    return {
        "bierdeckel_id": bd.id,
        "weight": bd.weight,
        "status": bd.status,
        "last_updated": str(bd.last_updated),
        "auto_ordered": auto_ordered
    }

# Alle Bierdeckel eines Restaurants (Dashboard)
@router.get("/restaurant/{restaurant_id}/bierdeckel")
def get_all_bierdeckel(restaurant_id: str, db: Session = Depends(get_db)):
    bierdeckel = db.query(Bierdeckel).filter(
        Bierdeckel.restaurant_id == restaurant_id
    ).all()

    result = []
    for bd in bierdeckel:
        table = db.query(Table).filter(Table.id == bd.table_id).first()
        result.append({
            "bierdeckel_id": bd.id,
            "label": bd.label,
            "table_number": table.table_number if table else None,
            "weight": bd.weight,
            "status": bd.status,
            "last_updated": str(bd.last_updated)
        })
    return result