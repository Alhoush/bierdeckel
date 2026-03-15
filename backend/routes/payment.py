from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database.db import get_db
from models.payment import Payment
from models.order import Order, OrderItem
from models.session import TableSession
from models.menu import MenuItem
from models.table import Table

router = APIRouter()

# Rechnung anzeigen (mit Artikeln)
@router.get("/session/{session_id}/bill")
def get_bill(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    orders = db.query(Order).filter(Order.session_id == session_id).all()

    items_list = []
    total = 0
    for order in orders:
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for oi in order_items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == oi.menu_item_id).first()

            # Quelle bestimmen
            if order.source == "game_loser":
                source_label = "🎮 Spiel (du zahlst)"
            elif order.source == "game_winner":
                source_label = "🎮 Spiel (gratis!)"
            else:
                source_label = None

            items_list.append({
                "name": menu_item.name if menu_item else "Unbekannt",
                "quantity": oi.quantity,
                "price": oi.price,
                "subtotal": oi.price * oi.quantity,
                "source": order.source,
                "source_label": source_label
            })
            total += oi.price * oi.quantity

    payments = db.query(Payment).filter(
        Payment.session_id == session_id,
        Payment.status == "completed"
    ).all()
    already_paid = sum(p.amount for p in payments)

    return {
        "session_id": session_id,
        "items": items_list,
        "total": total,
        "already_paid": already_paid,
        "remaining": total - already_paid
    }

# Einzelzahlung
@router.post("/session/{session_id}/pay")
def pay_single(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    orders = db.query(Order).filter(Order.session_id == session_id).all()
    total = sum(o.total for o in orders)

    payments = db.query(Payment).filter(
        Payment.session_id == session_id,
        Payment.status == "completed"
    ).all()
    already_paid = sum(p.amount for p in payments)
    remaining = total - already_paid

    if remaining <= 0:
        raise HTTPException(status_code=400, detail="Bereits alles bezahlt")

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

# Zahlungswunsch senden (Kellner rufen)
@router.post("/session/{session_id}/payment-request")
def request_payment(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    orders = db.query(Order).filter(Order.session_id == session_id).all()
    total = sum(o.total for o in orders)

    payments = db.query(Payment).filter(
        Payment.session_id == session_id,
        Payment.status == "completed"
    ).all()
    already_paid = sum(p.amount for p in payments)
    remaining = total - already_paid

    payment = Payment(
        session_id=session_id,
        amount=remaining,
        payment_type="single",
        status="requested"
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "payment_id": payment.id,
        "amount": remaining,
        "status": "requested",
        "message": "Zahlungswunsch an Kellner gesendet!"
    }

# Offene Zahlungswünsche (Dashboard)
@router.get("/restaurant/{restaurant_id}/payment-requests")
def get_payment_requests(restaurant_id: str, db: Session = Depends(get_db)):
    sessions = db.query(TableSession).filter(
        TableSession.restaurant_id == restaurant_id,
        TableSession.is_active == True
    ).all()
    session_ids = [s.id for s in sessions]

    payments = db.query(Payment).filter(
        Payment.session_id.in_(session_ids),
        Payment.status == "requested"
    ).all()

    result = []
    for p in payments:
        session = db.query(TableSession).filter(TableSession.id == p.session_id).first()
        table = db.query(Table).filter(Table.id == session.table_id).first()
        result.append({
            "payment_id": p.id,
            "session_id": p.session_id,
            "table_number": table.table_number if table else None,
            "amount": p.amount,
            "status": p.status,
            "created_at": str(p.created_at)
        })
    return result

# Kellner: Zahlung bestätigen
@router.put("/payment/{payment_id}/confirm")
def confirm_payment(payment_id: str, db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Zahlung nicht gefunden")

    payment.status = "completed"
    db.commit()

    return {
        "message": "Zahlung bestätigt!",
        "payment_id": payment_id,
        "amount": payment.amount,
        "status": "completed"
    }

# Für alle in der Gruppe bezahlen
@router.post("/session/{session_id}/pay-group")
def pay_for_group(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    if not session.group_id:
        raise HTTPException(status_code=400, detail="Du bist in keiner Gruppe")

    group_sessions = db.query(TableSession).filter(
        TableSession.group_id == session.group_id,
        TableSession.is_active == True
    ).all()

    total_paid = 0
    paid_sessions = []

    for gs in group_sessions:
        orders = db.query(Order).filter(Order.session_id == gs.id).all()
        total = sum(o.total for o in orders)

        payments = db.query(Payment).filter(
            Payment.session_id == gs.id,
            Payment.status == "completed"
        ).all()
        already_paid = sum(p.amount for p in payments)
        remaining = total - already_paid

        if remaining > 0:
            payment = Payment(
                session_id=gs.id,
                amount=remaining,
                payment_type="group",
                status="completed"
            )
            db.add(payment)
            total_paid += remaining

        table = db.query(Table).filter(Table.id == gs.table_id).first()
        paid_sessions.append({
            "session_id": gs.id,
            "table_number": table.table_number if table else None,
            "amount": remaining
        })

    db.commit()

    return {
        "message": f"Für alle bezahlt! Gesamt: {total_paid:.2f} €",
        "total_paid": total_paid,
        "paid_sessions": paid_sessions
    }

# Gruppen-Rechnung anzeigen
@router.get("/session/{session_id}/group-bill")
def get_group_bill(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(TableSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    if not session.group_id:
        raise HTTPException(status_code=400, detail="Du bist in keiner Gruppe")

    group_sessions = db.query(TableSession).filter(
        TableSession.group_id == session.group_id,
        TableSession.is_active == True
    ).all()

    group_total = 0
    group_items = []

    for gs in group_sessions:
        table = db.query(Table).filter(Table.id == gs.table_id).first()
        orders = db.query(Order).filter(Order.session_id == gs.id).all()

        for order in orders:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for oi in order_items:
                menu_item = db.query(MenuItem).filter(MenuItem.id == oi.menu_item_id).first()
                group_items.append({
                    "table_number": table.table_number if table else None,
                    "name": menu_item.name if menu_item else "Unbekannt",
                    "quantity": oi.quantity,
                    "price": oi.price,
                    "subtotal": oi.price * oi.quantity
                })
                group_total += oi.price * oi.quantity

    group_paid = 0
    for gs in group_sessions:
        payments = db.query(Payment).filter(
            Payment.session_id == gs.id,
            Payment.status == "completed"
        ).all()
        group_paid += sum(p.amount for p in payments)

    return {
        "group_total": group_total,
        "group_paid": group_paid,
        "group_remaining": group_total - group_paid,
        "items": group_items
    }