from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from database.db import get_db
from models.game import Game, GamePlayer
from models.session import TableSession
from models.order import Order, OrderItem
from models.menu import MenuItem
from models.table import Table

router = APIRouter()

class GameCreate(BaseModel):
    menu_item_id: str

class PlayerFinish(BaseModel):
    session_id: str

# Spiel erstellen
@router.post("/session/{session_id}/game/create")
def create_game(session_id: str, data: GameCreate, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    menu_item = db.query(MenuItem).filter(MenuItem.id == data.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Getränk nicht gefunden")

    new_game = Game(
        session_id=session_id,
        game_type="drink_race",
        status="waiting"
    )
    db.add(new_game)
    db.commit()
    db.refresh(new_game)

    player = GamePlayer(
        game_id=new_game.id,
        session_id=session_id,
        status="approved"
    )
    db.add(player)
    db.commit()

    table = db.query(Table).filter(Table.id == session.table_id).first()

    return {
        "game_id": new_game.id,
        "game_type": "drink_race",
        "drink": menu_item.name,
        "drink_id": menu_item.id,
        "status": "waiting",
        "table_number": table.table_number if table else None,
        "message": "Spiel erstellt! Warte auf Mitspieler."
    }

# Offene Spiele
@router.get("/restaurant/{restaurant_id}/games")
def get_open_games(restaurant_id: str, db: Session = Depends(get_db)):
    sessions = db.query(TableSession).filter(
        TableSession.restaurant_id == restaurant_id,
        TableSession.is_active == True
    ).all()
    session_ids = [s.id for s in sessions]

    if not session_ids:
        return []

    games = db.query(Game).filter(
        Game.session_id.in_(session_ids),
        Game.status == "waiting"
    ).all()

    result = []
    for game in games:
        creator_session = db.query(TableSession).filter(TableSession.id == game.session_id).first()
        table = db.query(Table).filter(Table.id == creator_session.table_id).first()
        players = db.query(GamePlayer).filter(
            GamePlayer.game_id == game.id,
            GamePlayer.status == "approved"
        ).all()

        result.append({
            "game_id": game.id,
            "creator_session_id": game.session_id,
            "table_number": table.table_number if table else None,
            "player_count": len(players),
            "created_at": str(game.created_at)
        })
    return result

# Beitritt anfragen
@router.post("/game/{game_id}/request-join/{session_id}")
def request_join(game_id: str, session_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")
    if game.status != "waiting":
        raise HTTPException(status_code=400, detail="Spiel akzeptiert keine Spieler mehr")

    existing = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.session_id == session_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bereits angefragt")

    player = GamePlayer(
        game_id=game_id,
        session_id=session_id,
        status="pending"
    )
    db.add(player)
    db.commit()

    return {"message": "Beitritt angefragt!", "game_id": game_id}

# Anfragen sehen
@router.get("/game/{game_id}/requests")
def get_join_requests(game_id: str, db: Session = Depends(get_db)):
    requests = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.status == "pending"
    ).all()

    result = []
    for r in requests:
        session = db.query(TableSession).filter(TableSession.id == r.session_id).first()
        table = db.query(Table).filter(Table.id == session.table_id).first()
        result.append({
            "player_id": r.id,
            "session_id": r.session_id,
            "table_number": table.table_number if table else None
        })
    return result

# Spieler genehmigen
@router.put("/game/{game_id}/approve/{player_id}")
def approve_player(game_id: str, player_id: str, db: Session = Depends(get_db)):
    player = db.query(GamePlayer).filter(
        GamePlayer.id == player_id,
        GamePlayer.game_id == game_id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    player.status = "approved"
    db.commit()
    return {"message": "Spieler genehmigt!"}

# Spieler ablehnen
@router.put("/game/{game_id}/decline/{player_id}")
def decline_player(game_id: str, player_id: str, db: Session = Depends(get_db)):
    player = db.query(GamePlayer).filter(
        GamePlayer.id == player_id,
        GamePlayer.game_id == game_id
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht gefunden")
    player.status = "declined"
    db.commit()
    return {"message": "Spieler abgelehnt"}

# Spiel starten
@router.put("/game/{game_id}/start")
def start_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")

    approved = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.status == "approved"
    ).all()

    if len(approved) < 2:
        raise HTTPException(status_code=400, detail="Mindestens 2 Spieler nötig")

    game.status = "active"
    db.commit()
    return {"message": "Spiel gestartet!", "game_id": game_id}

# Fertig getrunken
@router.post("/game/{game_id}/finish")
def player_finished(game_id: str, data: PlayerFinish, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")
    if game.status != "active":
        raise HTTPException(status_code=400, detail="Spiel ist nicht aktiv")

    player = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.session_id == data.session_id,
        GamePlayer.status == "approved"
    ).first()
    if not player:
        raise HTTPException(status_code=404, detail="Spieler nicht in diesem Spiel")
    if player.finished:
        raise HTTPException(status_code=400, detail="Bereits fertig")

    player.finished = True
    player.finished_at = datetime.utcnow()
    db.commit()

    all_players = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.status == "approved"
    ).all()
    not_finished = [p for p in all_players if not p.finished]

    if len(not_finished) == 1:
        loser = not_finished[0]
        game.loser_session_id = loser.session_id
        game.status = "finished"

        winners = [p for p in all_players if p.finished]
        extra_cost = 0

        for winner in winners:
            winner_orders = db.query(Order).filter(
                Order.session_id == winner.session_id,
                Order.status == "delivered"
            ).all()

            drink_price = 0
            drink_item_id = None
            found_item = None
            found_order = None

            for wo in winner_orders:
                items = db.query(OrderItem).filter(
                    OrderItem.order_id == wo.id
                ).all()
                for item in items:
                    drink_price = item.price
                    drink_item_id = item.menu_item_id
                    found_item = item
                    found_order = wo
                    break
                if found_item:
                    break

            if found_item and drink_item_id:
                # Getränk auf Verlierer-Rechnung (markiert als Spiel)
                loser_order = Order(
                    session_id=loser.session_id,
                    total=drink_price,
                    status="delivered",
                    source="game_loser"
                )
                db.add(loser_order)
                db.flush()

                loser_item = OrderItem(
                    order_id=loser_order.id,
                    menu_item_id=drink_item_id,
                    quantity=1,
                    price=drink_price
                )
                db.add(loser_item)
                extra_cost += drink_price

                # Gewinner-Getränk als "vom Spiel bezahlt" markieren
                if found_item.quantity > 1:
                    found_item.quantity -= 1
                    found_order.total = found_order.total - drink_price
                else:
                    found_order.total = found_order.total - drink_price
                    db.delete(found_item)

                # Gutschrift-Order für Gewinner
                winner_credit = Order(
                    session_id=winner.session_id,
                    total=0,
                    status="delivered",
                    source="game_winner"
                )
                db.add(winner_credit)
                db.flush()

                if found_order.total <= 0:
                    found_order.total = 0

        db.commit()

        # Spielstatistik aktualisieren
        try:
            from models.customer_stats import CustomerStats
            for p in all_players:
                p_session = db.query(TableSession).filter(TableSession.id == p.session_id).first()
                if p_session and p_session.customer_id:
                    stats = db.query(CustomerStats).filter(
                        CustomerStats.customer_id == p_session.customer_id,
                        CustomerStats.restaurant_id == p_session.restaurant_id
                    ).first()
                    if not stats:
                        stats = CustomerStats(
                            customer_id=p_session.customer_id,
                            restaurant_id=p_session.restaurant_id,
                            games_played=0,
                            games_won=0,
                            games_lost=0,
                            total_spent=0
                        )
                        db.add(stats)
                        db.flush()
                    stats.games_played += 1
                    if p.session_id == loser.session_id:
                        stats.games_lost += 1
                        stats.total_spent += extra_cost
                    else:
                        stats.games_won += 1
            db.commit()
        except Exception as e:
            print(f"Stats error: {e}")

        return {
            "message": "Spiel beendet! Verlierer zahlt die Getränke!",
            "loser_session_id": loser.session_id,
            "extra_cost": extra_cost,
            "game_status": "finished"
        }

    return {
        "message": "Fertig! Warte auf andere...",
        "remaining_players": len(not_finished),
        "game_status": "active"
    }

# Spielstatus
@router.get("/game/{game_id}")
def get_game(game_id: str, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")

    players = db.query(GamePlayer).filter(
        GamePlayer.game_id == game_id,
        GamePlayer.status == "approved"
    ).all()

    player_list = []
    for p in players:
        session = db.query(TableSession).filter(TableSession.id == p.session_id).first()
        table = db.query(Table).filter(Table.id == session.table_id).first()
        player_list.append({
            "session_id": p.session_id,
            "table_number": table.table_number if table else None,
            "finished": p.finished,
            "finished_at": str(p.finished_at) if p.finished_at else None
        })

    return {
        "game_id": game.id,
        "game_type": game.game_type,
        "status": game.status,
        "creator_session_id": game.session_id,
        "loser_session_id": game.loser_session_id,
        "players": player_list
    }