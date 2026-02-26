from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database.db import get_db
from models.bierdeckel import Bierdeckel
from models.table import Table

router = APIRouter()

class WeightUpdate(BaseModel):
    table_id: str
    weight: float  # Gewicht in Gramm

# Gewicht zu Füllstand umrechnen
def weight_to_status(weight: float) -> str:
    if weight < 50:
        return "empty"
    elif weight < 200:
        return "low"
    elif weight < 350:
        return "half"
    else:
        return "full"

# --- MQTT Bridge schickt Daten hierher ---
@router.post("/bierdeckel/update")
def update_weight(data: WeightUpdate, db: Session = Depends(get_db)):
    table = db.query(Table).filter(Table.id == data.table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Tisch nicht gefunden")

    # Bierdeckel suchen oder neu erstellen
    bierdeckel = db.query(Bierdeckel).filter(
        Bierdeckel.table_id == data.table_id
    ).first()

    if not bierdeckel:
        bierdeckel = Bierdeckel(
            table_id=data.table_id,
            restaurant_id=table.restaurant_id
        )
        db.add(bierdeckel)

    bierdeckel.weight = data.weight
    bierdeckel.status = weight_to_status(data.weight)
    bierdeckel.last_updated = datetime.utcnow()
    db.commit()
    db.refresh(bierdeckel)

    return {
        "table_id": data.table_id,
        "weight": bierdeckel.weight,
        "status": bierdeckel.status,
        "last_updated": str(bierdeckel.last_updated)
    }

# --- Einzelner Bierdeckel Status ---
@router.get("/bierdeckel/{table_id}")
def get_bierdeckel(table_id: str, db: Session = Depends(get_db)):
    bierdeckel = db.query(Bierdeckel).filter(
        Bierdeckel.table_id == table_id
    ).first()
    if not bierdeckel:
        return {"table_id": table_id, "status": "no_data"}

    return {
        "table_id": bierdeckel.table_id,
        "weight": bierdeckel.weight,
        "status": bierdeckel.status,
        "last_updated": str(bierdeckel.last_updated)
    }

# --- Alle Bierdeckel eines Restaurants (Dashboard) ---
@router.get("/restaurant/{restaurant_id}/bierdeckel")
def get_all_bierdeckel(restaurant_id: str, db: Session = Depends(get_db)):
    bierdeckel = db.query(Bierdeckel).filter(
        Bierdeckel.restaurant_id == restaurant_id
    ).all()

    result = []
    for b in bierdeckel:
        table = db.query(Table).filter(Table.id == b.table_id).first()
        result.append({
            "table_number": table.table_number if table else None,
            "table_id": b.table_id,
            "weight": b.weight,
            "status": b.status,
            "last_updated": str(b.last_updated)
        })
    return result