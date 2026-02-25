from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from models.restaurant import Restaurant

router = APIRouter()

# Request-Model (was der Client schickt)
class RestaurantCreate(BaseModel):
    name: str
    address: str = None
    logo_url: str = None

# Restaurant erstellen
@router.post("/restaurant")
def create_restaurant(data: RestaurantCreate, db: Session = Depends(get_db)):
    new_restaurant = Restaurant(
        name=data.name,
        address=data.address,
        logo_url=data.logo_url
    )
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)
    return {
        "id": new_restaurant.id,
        "name": new_restaurant.name,
        "address": new_restaurant.address,
        "logo_url": new_restaurant.logo_url,
        "created_at": str(new_restaurant.created_at)
    }

# Restaurant abrufen
@router.get("/restaurant/{restaurant_id}")
def get_restaurant(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant nicht gefunden")
    return {
        "id": restaurant.id,
        "name": restaurant.name,
        "address": restaurant.address,
        "logo_url": restaurant.logo_url,
        "created_at": str(restaurant.created_at)
    }

# Alle Restaurants auflisten
@router.get("/restaurants")
def get_all_restaurants(db: Session = Depends(get_db)):
    restaurants = db.query(Restaurant).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "address": r.address
        }
        for r in restaurants
    ]