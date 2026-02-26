from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database.db import get_db
from models.session import TableSession
from models.table import Table
from models.order import Order, OrderItem
from models.menu import MenuItem
from models.payment import Payment
from models.restaurant import Restaurant

router = APIRouter()

class ServiceRequest(BaseModel):
    request_type: str  # "waiter", "napkins", "other"
    message: str = None

# --- Serviceanfrage Model ---
from sqlalchemy import Column, String, DateTime, ForeignKey
from database.db import Base, engine
from datetime import datetime
import uuid

class ServiceCall(Base):
    __tablename__ = "service_calls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    request_type = Column(String, nullable=False)
    message = Column(String)
    status = Column(String, default="open")  # open, in_progress, done
    created_at = Column(DateTime, default=datetime.utcnow)

ServiceCall.__table__.create(bind=engine, checkfirst=True)

# --- Gast: Serviceanfrage senden ---
@router.post("/session/{session_id}/service-request")
def send_service_request(session_id: str, data: ServiceRequest, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    new_request = ServiceCall(
        session_id=session_id,
        restaurant_id=session.restaurant_id,
        request_type=data.request_type,
        message=data.message
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "message": "Serviceanfrage gesendet!",
        "request_id": new_request.id,
        "request_type": new_request.request_type
    }

# --- Service: Alle offenen Anfragen sehen ---
@router.get("/restaurant/{restaurant_id}/service-requests")
def get_service_requests(restaurant_id: str, db: Session = Depends(get_db)):
    requests = db.query(ServiceCall).filter(
        ServiceCall.restaurant_id == restaurant_id,
        ServiceCall.status != "done"
    ).all()

    result = []
    for r in requests:
        session = db.query(TableSession).filter(TableSession.id == r.session_id).first()
        table = db.query(Table).filter(Table.id == session.table_id).first()
        result.append({
            "request_id": r.id,
            "table_number": table.table_number if table else None,
            "request_type": r.request_type,
            "message": r.message,
            "status": r.status,
            "created_at": str(r.created_at)
        })
    return result

# --- Service: Anfrage-Status ändern ---
@router.put("/service-request/{request_id}/status/{status}")
def update_service_status(request_id: str, status: str, db: Session = Depends(get_db)):
    if status not in ["open", "in_progress", "done"]:
        raise HTTPException(status_code=400, detail="Ungültiger Status")

    request = db.query(ServiceCall).filter(ServiceCall.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

    request.status = status
    db.commit()
    return {"message": f"Status auf '{status}' gesetzt"}

# --- Service: Dashboard Übersicht ---
@router.get("/restaurant/{restaurant_id}/dashboard")
def get_dashboard(restaurant_id: str, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant nicht gefunden")

    # Alle Tische
    tables = db.query(Table).filter(Table.restaurant_id == restaurant_id).all()

    dashboard = []
    for table in tables:
        # Aktive Sessions am Tisch
        sessions = db.query(TableSession).filter(
            TableSession.table_id == table.id,
            TableSession.is_active == True
        ).all()

        table_data = {
            "table_number": table.table_number,
            "table_id": table.id,
            "active_guests": len(sessions),
            "sessions": []
        }

        for session in sessions:
            # Offene Bestellungen
            orders = db.query(Order).filter(
                Order.session_id == session.id,
                Order.status != "delivered"
            ).all()

            # Gesamtrechnung
            all_orders = db.query(Order).filter(Order.session_id == session.id).all()
            total = sum(o.total for o in all_orders)

            # Bezahlt
            payments = db.query(Payment).filter(
                Payment.session_id == session.id,
                Payment.status == "completed"
            ).all()
            paid = sum(p.amount for p in payments)

            # Offene Serviceanfragen
            open_requests = db.query(ServiceCall).filter(
                ServiceCall.session_id == session.id,
                ServiceCall.status != "done"
            ).all()

            table_data["sessions"].append({
                "session_id": session.id,
                "open_orders": len(orders),
                "total": total,
                "paid": paid,
                "remaining": total - paid,
                "open_service_requests": len(open_requests),
                "created_at": str(session.created_at)
            })

        dashboard.append(table_data)

    return {
        "restaurant": restaurant.name,
        "tables": dashboard
    }