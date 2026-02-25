from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.db import get_db
from models.menu import MenuItem

router = APIRouter()

class MenuItemCreate(BaseModel):
    name: str
    description: str = None
    price: float
    category: str
    image_url: str = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None

# Menü-Item erstellen (Owner/Admin)
@router.post("/restaurant/{restaurant_id}/menu")
def create_menu_item(restaurant_id: str, data: MenuItemCreate, db: Session = Depends(get_db)):
    new_item = MenuItem(
        name=data.name,
        description=data.description,
        price=data.price,
        category=data.category,
        image_url=data.image_url,
        restaurant_id=restaurant_id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return {
        "id": new_item.id,
        "name": new_item.name,
        "description": new_item.description,
        "price": new_item.price,
        "category": new_item.category,
        "image_url": new_item.image_url,
        "is_available": new_item.is_available
    }

# Ganzes Menü abrufen (Gäste sehen das)
@router.get("/restaurant/{restaurant_id}/menu")
def get_menu(restaurant_id: str, db: Session = Depends(get_db)):
    items = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.is_available == True
    ).all()

    # Nach Kategorie gruppieren
    menu = {}
    for item in items:
        if item.category not in menu:
            menu[item.category] = []
        menu[item.category].append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "image_url": item.image_url
        })
    return menu

# Menü-Item bearbeiten
@router.put("/menu/{item_id}")
def update_menu_item(item_id: str, data: MenuItemUpdate, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menü-Item nicht gefunden")

    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.price is not None:
        item.price = data.price
    if data.category is not None:
        item.category = data.category
    if data.image_url is not None:
        item.image_url = data.image_url
    if data.is_available is not None:
        item.is_available = data.is_available

    db.commit()
    return {"message": "Menü-Item aktualisiert"}

# Menü-Item löschen
@router.delete("/menu/{item_id}")
def delete_menu_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menü-Item nicht gefunden")

    db.delete(item)
    db.commit()
    return {"message": "Menü-Item gelöscht"}