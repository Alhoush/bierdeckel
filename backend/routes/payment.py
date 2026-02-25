from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database.db import get_db
from models.payment import Payment
from models.order import Order
from models.session import TableSession
from models.table import Table

router = APIRouter()

# Einzelzahlung
@router.post("/session/{session_id}/pay")
def pay_single(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    # Alle unbezahlten Bestellungen dieser Session
    orders = db.query(Order).filter(
        Order.session_id == session_id,
        Order.status != "cancelled"
    ).all()

    total = sum(order.total for order in orders)

    # Prüfen ob schon bezahlt
    existing_payments = db.query(Payment).filter(
        Payment.session_id == session_id,
        Payment.status == "completed"
    ).all()
    already_paid = sum(p.amount for p in existing_payments)

    remaining = total - already_paid
    if remaining <= 0:
        return {"message": "Bereits alles bezahlt", "total": total}

    # Zahlung erstellen
    payment = Payment(
        session_id=session_id,
        amount=remaining,
        payment_type="single",
        status="completed"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "session_id": session_id,
        "amount": remaining,
        "payment_type": "single",
        "status": "completed"
    }

# Gruppenzahlung (mehrere Sessions an einem Tisch)
class GroupPayRequest(BaseModel):
    session_ids: List[str]

@router.post("/pay/group")
def pay_group(data: GroupPayRequest, db: Session = Depends(get_db)):
    total = 0
    session_details = []

    for sid in data.session_ids:
        session = db.query(TableSession).filter(TableSession.id == sid).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {sid} nicht gefunden")

        orders = db.query(Order).filter(
            Order.session_id == sid,
            Order.status != "cancelled"
        ).all()
        session_total = sum(order.total for order in orders)

        # Bereits bezahlte Beträge abziehen
        existing_payments = db.query(Payment).filter(
            Payment.session_id == sid,
            Payment.status == "completed"
        ).all()
        already_paid = sum(p.amount for p in existing_payments)
        remaining = session_total - already_paid

        total += remaining
        session_details.append({
            "session_id": sid,
            "amount": remaining
        })

    if total <= 0:
        return {"message": "Bereits alles bezahlt"}

    # Zahlung für jede Session erstellen
    payments = []
    for detail in session_details:
        if detail["amount"] > 0:
            payment = Payment(
                session_id=detail["session_id"],
                amount=detail["amount"],
                payment_type="group",
                status="completed"
            )
            db.add(payment)
            payments.append(detail)

    db.commit()

    return {
        "total": total,
        "payment_type": "group",
        "status": "completed",
        "sessions": payments
    }

# Zahlungswunsch senden (Gast drückt "Ich möchte zahlen")
@router.post("/session/{session_id}/payment-request")
def request_payment(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    payment = Payment(
        session_id=session_id,
        amount=0,
        payment_type="single",
        status="requested"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Zahlungswunsch gesendet",
        "payment_id": payment.id,
        "session_id": session_id
    }

# Offene Zahlungswünsche für Restaurant (Service-Dashboard)
@router.get("/restaurant/{restaurant_id}/payment-requests")
def get_payment_requests(restaurant_id: str, db: Session = Depends(get_db)):
    sessions = db.query(TableSession).filter(
        TableSession.restaurant_id == restaurant_id,
        TableSession.is_active == True
    ).all()

    session_ids = [s.id for s in sessions]
    requests = db.query(Payment).filter(
        Payment.session_id.in_(session_ids),
        Payment.status == "requested"
    ).all()

    result = []
    for r in requests:
        session = db.query(TableSession).filter(TableSession.id == r.session_id).first()
        table = db.query(Table).filter(Table.id == session.table_id).first()

        # Offener Betrag berechnen
        orders = db.query(Order).filter(Order.session_id == r.session_id).all()
        total = sum(o.total for o in orders)

        result.append({
            "payment_id": r.id,
            "table_number": table.table_number if table else None,
            "session_id": r.session_id,
            "open_amount": total,
            "created_at": str(r.created_at)
        })
    return result

# Rechnung einer Session anzeigen
@router.get("/session/{session_id}/bill")
def get_bill(session_id: str, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.session_id == session_id).all()

    total = sum(o.total for o in orders)

    existing_payments = db.query(Payment).filter(
        Payment.session_id == session_id,
        Payment.status == "completed"
    ).all()
    already_paid = sum(p.amount for p in existing_payments)

    return {
        "session_id": session_id,
        "total": total,
        "already_paid": already_paid,
        "remaining": total - already_paid
    }