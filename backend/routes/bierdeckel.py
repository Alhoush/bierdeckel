from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database.db import get_db
from models.bierdeckel import Bierdeckel
from models.table import Table
import qrcode
import io
import base64

router = APIRouter()

class BierdeckelCreate(BaseModel):
    label: str

class WeightUpdate(BaseModel):
    bierdeckel_id: str
    weight: float

def weight_to_status(weight: float) -> str:
    if weight < 50:
        return "empty"
    elif weight < 200:
        return "low"
    elif weight < 350:
        return "half"
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
    qr_url = f"http://localhost:3000/r/{table.restaurant_id}/bd/{new_bd.id}"
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

    return {
        "bierdeckel_id": bd.id,
        "weight": bd.weight,
        "status": bd.status,
        "last_updated": str(bd.last_updated)
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