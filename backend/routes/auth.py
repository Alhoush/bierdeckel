from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import bcrypt
from jose import jwt
from datetime import datetime, timedelta
import uuid
from database.db import get_db
from models.user import User
from models.restaurant import Restaurant

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())
router = APIRouter()


SECRET_KEY = "bierdeckel-secret-key-2026"
ALGORITHM = "HS256"

# --- Request Models ---

class RegisterOwner(BaseModel):
    username: str
    password: str
    restaurant_name: str
    restaurant_address: str = None

class RegisterStaff(BaseModel):
    username: str
    password: str
    role: str = "staff"  # "staff" oder "admin"

class LoginRequest(BaseModel):
    username: str
    password: str

# --- Hilfsfunktion: Token prüfen ---

def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="User nicht gefunden")
        return user
    except:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

# --- Owner registrieren (erstellt Restaurant + Account) ---

@router.post("/auth/register-owner")
def register_owner(data: RegisterOwner, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username existiert bereits")

    # Restaurant erstellen
    new_restaurant = Restaurant(
        name=data.restaurant_name,
        address=data.restaurant_address
    )
    db.add(new_restaurant)
    db.commit()
    db.refresh(new_restaurant)

    # Owner-Account erstellen
    new_user = User(
        id=str(uuid.uuid4()),
        username=data.username,
        password_hash=hash_password(data.password),
        role="owner",
        restaurant_id=new_restaurant.id
    )
    db.add(new_user)
    db.commit()

    return {
        "message": "Restaurant und Owner erstellt",
        "restaurant_id": new_restaurant.id,
        "username": new_user.username,
        "role": new_user.role
    }

# --- Staff registrieren (nur Owner kann das) ---

@router.post("/auth/register-staff/{restaurant_id}")
def register_staff(restaurant_id: str, data: RegisterStaff, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username existiert bereits")

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant nicht gefunden")

    new_user = User(
        id=str(uuid.uuid4()),
        username=data.username,
        password_hash=pwd_context.hash(data.password),
        role=data.role,
        restaurant_id=restaurant_id
    )
    db.add(new_user)
    db.commit()

    return {
        "message": "Mitarbeiter erstellt",
        "username": new_user.username,
        "role": new_user.role,
        "restaurant_id": restaurant_id
    }

# --- Login ---

@router.post("/auth/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Falsche Zugangsdaten")

    token = jwt.encode(
        {
            "user_id": user.id,
            "role": user.role,
            "restaurant_id": user.restaurant_id,
            "exp": datetime.utcnow() + timedelta(hours=8)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "token": token,
        "role": user.role,
        "restaurant_id": user.restaurant_id
    }