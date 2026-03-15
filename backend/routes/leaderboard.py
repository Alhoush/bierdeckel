from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.customer_stats import CustomerStats
from models.customer import Customer

router = APIRouter()

# Rangliste (pro Restaurant)
@router.get("/restaurant/{restaurant_id}/leaderboard")
def get_leaderboard(restaurant_id: str, sort_by: str = "wins", db: Session = Depends(get_db)):
    stats = db.query(CustomerStats).filter(
        CustomerStats.restaurant_id == restaurant_id,
        CustomerStats.games_played > 0
    ).all()

    result = []
    for s in stats:
        customer = db.query(Customer).filter(Customer.id == s.customer_id).first()
        if not customer:
            continue

        win_rate = (s.games_won / s.games_played * 100) if s.games_played > 0 else 0

        result.append({
            "customer_id": s.customer_id,
            "display_name": customer.display_name,
            "avatar_url": f"/uploads/avatars/{customer.avatar_path}" if customer.avatar_path else None,
            "games_played": s.games_played,
            "games_won": s.games_won,
            "games_lost": s.games_lost,
            "win_rate": round(win_rate, 1),
            "total_spent": s.total_spent
        })

    if sort_by == "wins":
        result.sort(key=lambda x: x["games_won"], reverse=True)
    elif sort_by == "winrate":
        result.sort(key=lambda x: x["win_rate"], reverse=True)

    # Rang hinzufügen
    for i, r in enumerate(result):
        r["rank"] = i + 1

    return result

# Eigene Statistik
@router.get("/customer/{customer_id}/stats")
def get_customer_stats(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")

    stats = db.query(CustomerStats).filter(
        CustomerStats.customer_id == customer_id
    ).all()

    result = []
    for s in stats:
        from models.restaurant import Restaurant
        restaurant = db.query(Restaurant).filter(Restaurant.id == s.restaurant_id).first()
        win_rate = (s.games_won / s.games_played * 100) if s.games_played > 0 else 0

        result.append({
            "restaurant_id": s.restaurant_id,
            "restaurant_name": restaurant.name if restaurant else "Unbekannt",
            "games_played": s.games_played,
            "games_won": s.games_won,
            "games_lost": s.games_lost,
            "win_rate": round(win_rate, 1),
            "total_spent": s.total_spent
        })

    return result