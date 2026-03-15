from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database.db import get_db
from models.customer import Customer
from models.session import TableSession
from models.order import Order, OrderItem
from models.menu import MenuItem
from models.table import Table
from models.loyalty import CustomerLoyalty, LoyaltyProgram
import bcrypt
import uuid
import os
import shutil

router = APIRouter()

UPLOAD_DIR = "uploads/avatars"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

class CustomerRegister(BaseModel):
    username: str
    password: str
    display_name: str
    email: Optional[str] = None

class CustomerLogin(BaseModel):
    username: str
    password: str

class ProfileUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None

class PasswordChange(BaseModel):
    old_password: str
    new_password: str

# Registrieren
@router.post("/customer/register")
def register_customer(data: CustomerRegister, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username bereits vergeben")

    customer = Customer(
        username=data.username,
        password=hash_password(data.password),
        display_name=data.display_name,
        email=data.email
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)

    return {
        "customer_id": customer.id,
        "username": customer.username,
        "display_name": customer.display_name,
        "message": "Konto erstellt!"
    }

# Einloggen
@router.post("/customer/login")
def login_customer(data: CustomerLogin, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.username == data.username).first()
    if not customer or not verify_password(data.password, customer.password):
        raise HTTPException(status_code=401, detail="Falsche Zugangsdaten")

    return {
        "customer_id": customer.id,
        "username": customer.username,
        "display_name": customer.display_name,
        "avatar_url": f"/uploads/avatars/{customer.id}.jpg" if customer.avatar_path else None
    }

# Session mit Konto verknüpfen
@router.put("/session/{session_id}/link-customer/{customer_id}")
def link_customer_to_session(session_id: str, customer_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    session.customer_id = customer_id
    db.commit()

    return {"message": "Konto mit Session verknüpft!", "session_id": session_id, "customer_id": customer_id}

# Profil abrufen
@router.get("/customer/{customer_id}/profile")
def get_profile(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    return {
        "customer_id": customer.id,
        "username": customer.username,
        "display_name": customer.display_name,
        "email": customer.email,
        "avatar_url": f"/uploads/avatars/{customer.id}.jpg" if customer.avatar_path else None,
        "created_at": str(customer.created_at)
    }

# Profil bearbeiten
@router.put("/customer/{customer_id}/profile")
def update_profile(customer_id: str, data: ProfileUpdate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    if data.display_name:
        customer.display_name = data.display_name
    if data.email is not None:
        customer.email = data.email

    db.commit()
    return {"message": "Profil aktualisiert!"}

# Profilbild hochladen
@router.put("/customer/{customer_id}/avatar")
async def upload_avatar(customer_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    # Dateityp prüfen
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Nur JPG, PNG oder WebP erlaubt")

    # Dateigröße prüfen (max 2MB)
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Bild darf max. 2MB groß sein")

    # Speichern
    ext = file.content_type.split("/")[1]
    if ext == "jpeg":
        ext = "jpg"
    filename = f"{customer_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    customer.avatar_path = filename
    db.commit()

    return {
        "message": "Profilbild hochgeladen!",
        "avatar_url": f"/uploads/avatars/{filename}"
    }

# Passwort ändern
@router.put("/customer/{customer_id}/password")
def change_password(customer_id: str, data: PasswordChange, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    if not verify_password(data.old_password, customer.password):
        raise HTTPException(status_code=401, detail="Altes Passwort falsch")

    customer.password = hash_password(data.new_password)
    db.commit()
    return {"message": "Passwort geändert!"}

# Konto löschen
@router.delete("/customer/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    # Avatar-Datei löschen
    if customer.avatar_path:
        filepath = os.path.join(UPLOAD_DIR, customer.avatar_path)
        if os.path.exists(filepath):
            os.remove(filepath)

    # Sessions entkoppeln
    sessions = db.query(TableSession).filter(TableSession.customer_id == customer_id).all()
    for s in sessions:
        s.customer_id = None

    db.delete(customer)
    db.commit()
    return {"message": "Konto gelöscht!"}

# Bestellhistorie (alle Besuche)
@router.get("/customer/{customer_id}/history")
def get_history(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    sessions = db.query(TableSession).filter(
        TableSession.customer_id == customer_id
    ).order_by(TableSession.created_at.desc()).all()

    history = []
    for session in sessions:
        table = db.query(Table).filter(Table.id == session.table_id).first()
        orders = db.query(Order).filter(Order.session_id == session.id).all()

        items = []
        total = 0
        for order in orders:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for oi in order_items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == oi.menu_item_id).first()
                items.append({
                    "name": menu_item.name if menu_item else "Unbekannt",
                    "quantity": oi.quantity,
                    "price": oi.price,
                    "subtotal": oi.price * oi.quantity
                })
                total += oi.price * oi.quantity

        from models.payment import Payment
        payments = db.query(Payment).filter(
            Payment.session_id == session.id,
            Payment.status == "completed"
        ).all()
        paid = sum(p.amount for p in payments)

        history.append({
            "session_id": session.id,
            "restaurant_id": session.restaurant_id,
            "table_number": table.table_number if table else None,
            "date": str(session.created_at),
            "items": items,
            "total": total,
            "paid": paid,
            "is_active": session.is_active
        })

    return history