from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database.db import get_db
from models.game import Game
from models.session import TableSession
from models.order import Order, OrderItem
from models.menu import MenuItem

router = APIRouter()

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from database.db import Base, engine
import uuid

class GamePlayer(Base):
    __tablename__ = "game_players"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    game_id = Column(String, ForeignKey("games.id"), nullable=False)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    finished = Column(Boolean, default=False)
    finished_at = Column(DateTime, nullable=True)

GamePlayer.__table__.create(bind=engine, checkfirst=True)

class GameCreate(BaseModel):
    session_ids: List[str]
    menu_item_id: str

class PlayerFinish(BaseModel):
    session_id: str

# Spiel erstellen
@router.post("/game/create")
def create_game(data: GameCreate, db: Session = Depends(get_db)):
    if len(data.session_ids) < 2:
        raise HTTPException(status_code=400, detail="Mindestens 2 Spieler nötig")

    menu_item = db.query(MenuItem).filter(MenuItem.id == data.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Getränk nicht gefunden")

    for sid in data.session_ids:
        session = db.query(TableSession).filter(
            TableSession.id == sid,
            TableSession.is_active == True
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {sid} nicht gefunden")

        orders = db.query(Order).filter(
            Order.session_id == sid,
            Order.status == "delivered"
        ).all()

        has_drink = False
        for order in orders:
            items = db.query(OrderItem).filter(
                OrderItem.order_id == order.id,
                OrderItem.menu_item_id == data.menu_item_id
            ).all()
            if items:
                has_drink = True
                break

        if not has_drink:
            raise HTTPException(
                status_code=400,
                detail=f"Session {sid} hat kein geliefertes '{menu_item.name}'. Erst bestellen und liefern lassen!"
            )

    new_game = Game(
        session_id=data.session_ids[0],
        game_type="drink_race",
        status="active"
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    players = []
    for sid in data.session_ids:
        player = GamePlayer(
            game_id=new_game.id,
            session_id=sid
        )
        db.add(player)
        players.append(sid)

    db.commit()

    return {
        "game_id": new_game.id,
        "game_type": "drink_race",
        "drink": menu_item.name,
        "status": "active",
        "players": players
    }

# Spieler ist fertig
@router.post("/game/{game_id}/finish")
def player_finished(game_id: str, data: PlayerFinish, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")
    if game.status == "finished":
        raise HTTPException(status_code=400, detail="Spiel ist bereits beendet")

    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.session_id == data.session_id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht in diesem Spiel")
    if player.finished:
        raise HTTPException(status_code=400, detail="Spieler hat bereits beendet")

    player.finished = True
    player.finished_at = datetime.utcnow()
    db.commit()

    all_players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    not_finished = [p for p in all_players if not p.finished]

    if len(not_finished) == 1:
        loser = not_finished[0]
        game.loser_session_id = loser.session_id
        game.status = "finished"

        # Gewinner-Getränke auf Verlierer-Rechnung buchen
        winners = [p for p in all_players if p.finished]
        extra_cost = 0

        for winner in winners:
            winner_orders = db.query(Order).filter(
                Order.session_id == winner.session_id,
                Order.status == "delivered"
            ).all()

            drink_price = 0
            drink_item_id = None

            for wo in winner_orders:
                items = db.query(OrderItem).filter(
                    OrderItem.order_id == wo.id
                ).all()
                for item in items:
                    drink_price = item.price
                    drink_item_id = item.menu_item_id
                    break
                if drink_item_id:
                    break

            if drink_item_id:
                # Getränk auf Verlierer-Rechnung buchen
                loser_order = Order(
                    session_id=loser.session_id,
                    total=drink_price,
                    status="delivered"
                )
                db.add(loser_order)
                db.commit()
                db.refresh(loser_order)

                loser_item = OrderItem(
                    order_id=loser_order.id,
                    menu_item_id=drink_item_id,
                    quantity=1,
                    price=drink_price
                )
                db.add(loser_item)
                extra_cost += drink_price

        # Gewinner-Getränke von deren Rechnung entfernen
        for winner in winners:
            winner_orders = db.query(Order).filter(
                Order.session_id == winner.session_id,
                Order.status == "delivered"
            ).all()

            for wo in winner_orders:
                items = db.query(OrderItem).filter(
                    OrderItem.order_id == wo.id
                ).all()
                if items:
                    wo.total = wo.total - items[0].price
                    db.delete(items[0])
                    break

        db.commit()

        return {
            "message": "Spiel beendet! Verlierer zahlt die Getränke der Gewinner!",
            "loser_session_id": loser.session_id,
            "extra_cost": extra_cost,
            "game_status": "finished"
        }

    return {
        "message": "Fertig! Warte auf andere Spieler...",
        "remaining_players": len(not_finished),
        "game_status": "active"
    }

# Spielstatus abrufen
@router.get("/game/{game_id}")
def get_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")

    players = db.query(GamePlayer).filter(GamePlayer.game_id == game_id).all()
    player_list = []
    for p in players:
        player_list.append({
            "session_id": p.session_id,
            "finished": p.finished,
            "finished_at": str(p.finished_at) if p.finished_at else None
        })

    return {
        "game_id": game.id,
        "game_type": game.game_type,
        "status": game.status,
        "loser_session_id": game.loser_session_id,
        "players": player_list
    }