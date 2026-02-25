from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from models.table import Table
from models.restaurant import Restaurant
import qrcode
import io
import base64

router = APIRouter()

class TableCreate(BaseModel):
    table_number: int

# Tisch erstellen + QR-Code generieren
@router.post("/restaurant/{restaurant_id}/table")
def create_table(restaurant_id: str, data: TableCreate, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant nicht gefunden")

    # Prüfen ob Tischnummer schon existiert
    existing = db.query(Table).filter(
        Table.restaurant_id == restaurant_id,
        Table.table_number == data.table_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tischnummer existiert bereits")

    # QR-Code URL erstellen
    qr_url = f"https://bierdeckel.app/r/{restaurant_id}/table/{data.table_number}"

    new_table = Table(
        table_number=data.table_number,
        qr_code=qr_url,
        restaurant_id=restaurant_id
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table)

    return {
        "id": new_table.id,
        "table_number": new_table.table_number,
        "qr_code_url": new_table.qr_code,
        "restaurant_id": restaurant_id
    }

# QR-Code als Bild abrufen
@router.get("/table/{table_id}/qr")
def get_qr_code(table_id: str, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Tisch nicht gefunden")

    # QR-Code Bild generieren
    qr = qrcode.make(table.qr_code)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {
        "table_number": table.table_number,
        "qr_code_url": table.qr_code,
        "qr_code_image": f"data:image/png;base64,{qr_base64}"
    }

# Alle Tische eines Restaurants
@router.get("/restaurant/{restaurant_id}/tables")
def get_tables(restaurant_id: str, db: Session = Depends(get_db)):
    tables = db.query(Table).filter(Table.restaurant_id == restaurant_id).all()
    return [
        {
            "id": t.id,
            "table_number": t.table_number,
            "qr_code_url": t.qr_code
        }
        for t in tables
    ]