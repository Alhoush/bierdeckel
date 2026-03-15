from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.db import get_db
from models.loyalty import LoyaltyProgram, CustomerLoyalty
from models.menu import MenuItem
from models.customer import Customer

router = APIRouter()

class LoyaltyCreate(BaseModel):
    name: str
    required_orders: int = 10
    reward_type: str = "free_drink"  # free_drink, discount
    discount_percent: Optional[float] = None
    menu_item_id: Optional[str] = None

class LoyaltyUpdate(BaseModel):
    name: Optional[str] = None
    required_orders: Optional[int] = None
    reward_type: Optional[str] = None
    discount_percent: Optional[float] = None
    is_active: Optional[bool] = None

# Treueprogramm erstellen (Admin)
@router.post("/restaurant/{restaurant_id}/loyalty")
def create_loyalty(restaurant_id: str, data: LoyaltyCreate, db: Session = Depends(get_db)):
    program = LoyaltyProgram(
        restaurant_id=restaurant_id,
        name=data.name,
        required_orders=data.required_orders,
        reward_type=data.reward_type,
        discount_percent=data.discount_percent,
        menu_item_id=data.menu_item_id
    )
    db.add(program)
    db.commit()
    db.refresh(program)

    menu_item = None
    if program.menu_item_id:
        menu_item = db.query(MenuItem).filter(MenuItem.id == program.menu_item_id).first()

    return {
        "id": program.id,
        "name": program.name,
        "required_orders": program.required_orders,
        "reward_type": program.reward_type,
        "discount_percent": program.discount_percent,
        "menu_item": menu_item.name if menu_item else "Alle Getränke",
        "is_active": program.is_active
    }

# Treueprogramme abrufen (Restaurant)
@router.get("/restaurant/{restaurant_id}/loyalty")
def get_loyalty_programs(restaurant_id: str, db: Session = Depends(get_db)):
    programs = db.query(LoyaltyProgram).filter(
        LoyaltyProgram.restaurant_id == restaurant_id
    ).all()

    result = []
    for p in programs:
        menu_item = None
        if p.menu_item_id:
            menu_item = db.query(MenuItem).filter(MenuItem.id == p.menu_item_id).first()

        result.append({
            "id": p.id,
            "name": p.name,
            "required_orders": p.required_orders,
            "reward_type": p.reward_type,
            "discount_percent": p.discount_percent,
            "menu_item": menu_item.name if menu_item else "Alle Getränke",
            "is_active": p.is_active
        })
    return result

# Treueprogramm bearbeiten
@router.put("/loyalty/{program_id}")
def update_loyalty(program_id: str, data: LoyaltyUpdate, db: Session = Depends(get_db)):
    program = db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programm nicht gefunden")

    if data.name is not None:
        program.name = data.name
    if data.required_orders is not None:
        program.required_orders = data.required_orders
    if data.reward_type is not None:
        program.reward_type = data.reward_type
    if data.discount_percent is not None:
        program.discount_percent = data.discount_percent
    if data.is_active is not None:
        program.is_active = data.is_active

    db.commit()
    return {"message": "Programm aktualisiert!"}

# Treueprogramm löschen
@router.delete("/loyalty/{program_id}")
def delete_loyalty(program_id: str, db: Session = Depends(get_db)):
    program = db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programm nicht gefunden")

    # Zugehörige Kundenfortschritte löschen
    db.query(CustomerLoyalty).filter(CustomerLoyalty.loyalty_program_id == program_id).delete()
    db.delete(program)
    db.commit()
    return {"message": "Programm gelöscht!"}

# Kunden-Fortschritt abrufen
@router.get("/customer/{customer_id}/loyalty/{restaurant_id}")
def get_customer_loyalty(customer_id: str, restaurant_id: str, db: Session = Depends(get_db)):
    programs = db.query(LoyaltyProgram).filter(
        LoyaltyProgram.restaurant_id == restaurant_id,
        LoyaltyProgram.is_active == True
    ).all()

    result = []
    for p in programs:
        progress = db.query(CustomerLoyalty).filter(
            CustomerLoyalty.customer_id == customer_id,
            CustomerLoyalty.loyalty_program_id == p.id
        ).first()

        current = progress.current_count if progress else 0
        rewards = progress.rewards_claimed if progress else 0

        menu_item = None
        if p.menu_item_id:
            menu_item = db.query(MenuItem).filter(MenuItem.id == p.menu_item_id).first()

        reward_available = current >= p.required_orders

        result.append({
            "program_id": p.id,
            "name": p.name,
            "required_orders": p.required_orders,
            "current_count": current,
            "remaining": max(0, p.required_orders - current),
            "reward_available": reward_available,
            "reward_type": p.reward_type,
            "discount_percent": p.discount_percent,
            "menu_item": menu_item.name if menu_item else "Alle Getränke",
            "rewards_claimed": rewards
        })
    return result

# Belohnung einlösen
@router.post("/customer/{customer_id}/loyalty/{program_id}/claim")
def claim_reward(customer_id: str, program_id: str, db: Session = Depends(get_db)):
    progress = db.query(CustomerLoyalty).filter(
        CustomerLoyalty.customer_id == customer_id,
        CustomerLoyalty.loyalty_program_id == program_id
    ).first()

    if not progress:
        raise HTTPException(status_code=404, detail="Kein Fortschritt gefunden")

    program = db.query(LoyaltyProgram).filter(LoyaltyProgram.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Programm nicht gefunden")

    if progress.current_count < program.required_orders:
        raise HTTPException(status_code=400, detail=f"Noch {program.required_orders - progress.current_count} Bestellungen nötig")

    progress.current_count -= program.required_orders
    progress.rewards_claimed += 1
    db.commit()

    return {
        "message": "Belohnung eingelöst!",
        "reward_type": program.reward_type,
        "discount_percent": program.discount_percent,
        "rewards_claimed": progress.rewards_claimed,
        "remaining_count": progress.current_count
    }