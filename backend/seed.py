from database.db import SessionLocal
from models.restaurant import Restaurant
from models.user import User
from models.table import Table
from models.bierdeckel import Bierdeckel
from models.menu import MenuItem
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_database():
    db = SessionLocal()

    # Prüfen ob schon Daten existieren
    if db.query(Restaurant).first():
        print("Datenbank hat schon Daten - Seed übersprungen")
        db.close()
        return

    print("Seed: Datenbank wird befüllt...")

    # === RESTAURANT ===
    restaurant = Restaurant(
        id="restaurant-001",
        name="Biergarten München",
        address="Marienplatz 1"
    )
    db.add(restaurant)

    # === OWNER ===
    owner = User(
        id="owner-001",
        username="hans",
        password=hash_password("hans123"),
        role="owner",
        restaurant_id="restaurant-001"
    )
    db.add(owner)

    # === KELLNER ===
    kellner = User(
        id="staff-001",
        username="max",
        password=hash_password("max123"),
        role="staff",
        restaurant_id="restaurant-001"
    )
    db.add(kellner)

    # === TEAM ADMINS ===
    admins = [
        User(id="admin-001", username="jens", password=hash_password("jens123"), role="admin", restaurant_id="restaurant-001"),
        User(id="admin-002", username="alex", password=hash_password("alex123"), role="admin", restaurant_id="restaurant-001"),
        User(id="admin-003", username="chrissi", password=hash_password("chrissi123"), role="admin", restaurant_id="restaurant-001"),
        User(id="admin-004", username="mirek", password=hash_password("mirek123"), role="admin", restaurant_id="restaurant-001"),
    ]
    for a in admins:
        db.add(a)

    # === TISCHE ===
    tables = [
        Table(id="table-001", table_number=1, seats=4, restaurant_id="restaurant-001"),
        Table(id="table-002", table_number=2, seats=4, restaurant_id="restaurant-001"),
        Table(id="table-003", table_number=3, seats=2, restaurant_id="restaurant-001"),
    ]
    for t in tables:
        db.add(t)

    # === BIERDECKEL (FESTE IDs - NICHT ÄNDERN!) ===
    bierdeckel = [
        # Tisch 1
        Bierdeckel(
            id="bd-001",
            label="BD-001",
            table_id="table-001",
            restaurant_id="restaurant-001",
            qr_code="https://bierdeckel-8if9.vercel.app/r/restaurant-001/bd/bd-001"
        ),
        Bierdeckel(
            id="bd-002",
            label="BD-002",
            table_id="table-001",
            restaurant_id="restaurant-001",
            qr_code="https://bierdeckel-8if9.vercel.app/r/restaurant-001/bd/bd-002"
        ),
        # Tisch 2
        Bierdeckel(
            id="bd-003",
            label="BD-003",
            table_id="table-002",
            restaurant_id="restaurant-001",
            qr_code="https://bierdeckel-8if9.vercel.app/r/restaurant-001/bd/bd-003"
        ),
        Bierdeckel(
            id="bd-004",
            label="BD-004",
            table_id="table-002",
            restaurant_id="restaurant-001",
            qr_code="https://bierdeckel-8if9.vercel.app/r/restaurant-001/bd/bd-004"
        ),
        # Tisch 3
        Bierdeckel(
            id="bd-005",
            label="BD-005",
            table_id="table-003",
            restaurant_id="restaurant-001",
            qr_code="https://bierdeckel-8if9.vercel.app/r/restaurant-001/bd/bd-005"
        ),
        Bierdeckel(
            id="bd-006",
            label="BD-006",
            table_id="table-003",
            restaurant_id="restaurant-001",
            qr_code="https://bierdeckel-8if9.vercel.app/r/restaurant-001/bd/bd-006"
        ),
    ]
    for bd in bierdeckel:
        db.add(bd)

    # === MENÜ ===
    menu_items = [
        MenuItem(id="menu-001", name="Weißbier", description="Bayrisches Weißbier 0.5l", price=4.50, category="Bier", restaurant_id="restaurant-001"),
        MenuItem(id="menu-002", name="Helles", description="Münchner Helles 0.5l", price=3.90, category="Bier", restaurant_id="restaurant-001"),
        MenuItem(id="menu-003", name="Radler", description="Erfrischendes Radler 0.5l", price=3.50, category="Bier", restaurant_id="restaurant-001"),
        MenuItem(id="menu-004", name="Cola", description="Coca Cola 0.3l", price=2.80, category="Alkoholfrei", restaurant_id="restaurant-001"),
        MenuItem(id="menu-005", name="Spezi", description="Spezi 0.3l", price=2.80, category="Alkoholfrei", restaurant_id="restaurant-001"),
        MenuItem(id="menu-006", name="Wasser", description="Mineralwasser 0.5l", price=2.50, category="Alkoholfrei", restaurant_id="restaurant-001"),
        MenuItem(id="menu-007", name="Brezel", description="Frische Brezel mit Butter", price=3.20, category="Essen", restaurant_id="restaurant-001"),
        MenuItem(id="menu-008", name="Obatzda", description="Bayrischer Obatzda mit Brezel", price=5.90, category="Essen", restaurant_id="restaurant-001"),
    ]
    for item in menu_items:
        db.add(item)

    db.commit()
    db.close()

    print("Seed: Fertig! Daten erstellt:")
    print("  Owner: hans / hans123")
    print("  Kellner: max / max123")
    print("  3 Tische, 6 Bierdeckel, 8 Menü-Items")
    print("  Bierdeckel IDs: bd-001 bis bd-006")