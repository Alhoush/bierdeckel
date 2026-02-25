from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database.db import get_db
from models.order import Order, OrderItem
from models.menu import MenuItem
from models.session import TableSession

router = APIRouter()

class OrderItemCreate(BaseModel):
    menu_item_id: str
    quantity: int = 1

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]

# Bestellung aufgeben
@router.post("/session/{session_id}/order")
def create_order(session_id: str, data: OrderCreate, db: Session = Depends(get_db)):
    # Session prüfen
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden oder nicht aktiv")

    # Neue Bestellung erstellen
    new_order = Order(session_id=session_id)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    total = 0
    order_items = []

    for item in data.items:
        # Menü-Item prüfen
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menü-Item {item.menu_item_id} nicht gefunden")
        if not menu_item.is_available:
            raise HTTPException(status_code=400, detail=f"{menu_item.name} ist nicht verfügbar")

        item_total = menu_item.price * item.quantity
        total += item_total

        order_item = OrderItem(
            order_id=new_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price=menu_item.price
        )
        db.add(order_item)
        order_items.append({
            "name": menu_item.name,
            "quantity": item.quantity,
            "price": menu_item.price,
            "subtotal": item_total
        })

    # Total speichern
    new_order.total = total
    db.commit()

    return {
        "order_id": new_order.id,
        "session_id": session_id,
        "items": order_items,
        "total": total,
        "status": new_order.status,
        "created_at": str(new_order.created_at)
    }

# Bestellung abrufen
@router.get("/order/{order_id}")
def get_order(order_id: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

    items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    order_items = []
    for item in items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
        order_items.append({
            "name": menu_item.name if menu_item else "Unbekannt",
            "quantity": item.quantity,
            "price": item.price,
            "subtotal": item.price * item.quantity
        })

    return {
        "order_id": order.id,
        "session_id": order.session_id,
        "items": order_items,
        "total": order.total,
        "status": order.status,
        "created_at": str(order.created_at)
    }

# Bestellhistorie einer Session
@router.get("/session/{session_id}/orders")
def get_session_orders(session_id: str, db: Session = Depends(get_db)):
    orders = db.query(Order).filter(Order.session_id == session_id).all()
    result = []
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        order_items = []
        for item in items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            order_items.append({
                "name": menu_item.name if menu_item else "Unbekannt",
                "quantity": item.quantity,
                "price": item.price
            })
        result.append({
            "order_id": order.id,
            "items": order_items,
            "total": order.total,
            "status": order.status,
            "created_at": str(order.created_at)
        })
    return result

# Bestellstatus ändern (für Service)
@router.put("/order/{order_id}/status/{status}")
def update_order_status(order_id: str, status: str, db: Session = Depends(get_db)):
    if status not in ["pending", "preparing", "delivered"]:
        raise HTTPException(status_code=400, detail="Ungültiger Status")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Bestellung nicht gefunden")

    order.status = status
    db.commit()
    return {"message": f"Status auf '{status}' gesetzt", "order_id": order_id}

# Alle offenen Bestellungen eines Restaurants (für Service-Dashboard)
@router.get("/restaurant/{restaurant_id}/orders")
def get_restaurant_orders(restaurant_id: str, db: Session = Depends(get_db)):
    sessions = db.query(TableSession).filter(
        TableSession.restaurant_id == restaurant_id,
        TableSession.is_active == True
    ).all()

    session_ids = [s.id for s in sessions]
    orders = db.query(Order).filter(
        Order.session_id.in_(session_ids),
        Order.status != "delivered"
    ).all()

    result = []
    for order in orders:
        session = db.query(TableSession).filter(TableSession.id == order.session_id).first()
        from models.table import Table
        table = db.query(Table).filter(Table.id == session.table_id).first()

        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        order_items = []
        for item in items:
            menu_item = db.query(MenuItem).filter(MenuItem.id == item.menu_item_id).first()
            order_items.append({
                "name": menu_item.name if menu_item else "Unbekannt",
                "quantity": item.quantity
            })

        result.append({
            "order_id": order.id,
            "table_number": table.table_number if table else None,
            "items": order_items,
            "total": order.total,
            "status": order.status,
            "created_at": str(order.created_at)
        })
    return result