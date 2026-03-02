from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from models.table import Table
from models.restaurant import Restaurant

router = APIRouter()

class TableCreate(BaseModel):
    table_number: int
    seats: int = 4

@router.post("/restaurant/{restaurant_id}/table")
def create_table(restaurant_id: str, data: TableCreate, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant nicht gefunden")

    existing = db.query(Table).filter(
        Table.restaurant_id == restaurant_id,
        Table.table_number == data.table_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tischnummer existiert bereits")

    new_table = Table(
        table_number=data.table_number,
        seats=data.seats,
        restaurant_id=restaurant_id
    )
    db.add(new_table)
    db.commit()
    db.refresh(new_table)

    return {
        "id": new_table.id,
        "table_number": new_table.table_number,
        "seats": new_table.seats,
        "restaurant_id": restaurant_id
    }

@router.get("/restaurant/{restaurant_id}/tables")
def get_tables(restaurant_id: str, db: Session = Depends(get_db)):
    tables = db.query(Table).filter(Table.restaurant_id == restaurant_id).all()
    from models.bierdeckel import Bierdeckel
    result = []
    for t in tables:
        bierdeckel = db.query(Bierdeckel).filter(Bierdeckel.table_id == t.id).all()
        result.append({
            "id": t.id,
            "table_number": t.table_number,
            "seats": t.seats,
            "bierdeckel_count": len(bierdeckel)
        })
    return result