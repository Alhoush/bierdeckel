# 🍺 Bierdeckel / TabTracker – System Dokumentation

## Projektübersicht

TabTracker ist ein Multi-Restaurant Bestell- und Bezahlsystem. Jeder Gast scannt den QR-Code auf seinem Bierdeckel, bestellt über sein Handy und bezahlt digital. Der Service verwaltet alles über ein Dashboard.

---

## Architektur

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Bierdeckel     │     │   Kunden-App      │     │  Dashboard    │
│   (Hardware)     │     │   (React)         │     │  (React)      │
│   QR-Code +      │     │   Handy/Browser   │     │  PC/Tablet    │
│   Gewichtssensor │     │                   │     │               │
└───────┬──────────┘     └────────┬──────────┘     └───────┬───────┘
        │ MQTT                    │ HTTP                    │ HTTP
        ▼                         ▼                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                               │
│                     SQLite Datenbank                              │
└──────────────────────────────────────────────────────────────────┘
```

---

## Hierarchie: Restaurant → Tisch → Bierdeckel → Session

```
Restaurant "Biergarten München"
│
├── Tisch 1 (4 Plätze)
│   ├── Bierdeckel BD-001 → QR-Code → Gast A (Session)
│   ├── Bierdeckel BD-002 → QR-Code → Gast B (Session)
│   ├── Bierdeckel BD-003 → QR-Code → (leer)
│   └── Bierdeckel BD-004 → QR-Code → (leer)
│
├── Tisch 2 (2 Plätze)
│   ├── Bierdeckel BD-005 → QR-Code → Gast C (Session)
│   └── Bierdeckel BD-006 → QR-Code → (leer)
```

Jeder Bierdeckel hat einen eigenen QR-Code. Wenn ein Gast den QR-Code scannt, wird automatisch eine Session erstellt.

---

## Benutzerrollen

### 👑 Owner (Restaurantbesitzer)

| Funktion | Beschreibung |
|----------|-------------|
| Restaurant erstellen | Name, Adresse |
| Tische erstellen | Tischnummer, Anzahl Plätze |
| Bierdeckel erstellen | Label, QR-Code pro Bierdeckel |
| Menü verwalten | Getränke/Speisen hinzufügen, bearbeiten, löschen |
| Mitarbeiter anlegen | Kellner oder Admin erstellen |
| Dashboard | Alles sehen und verwalten |

### 🧑‍🍳 Admin

| Funktion | Beschreibung |
|----------|-------------|
| Gleich wie Owner | Tische, Menü, Personal verwalten |
| Dashboard | Alles sehen und verwalten |

### 👤 Kellner (Staff)

| Funktion | Beschreibung |
|----------|-------------|
| Dashboard sehen | Tische, Gäste, Bestellungen |
| Bestellungen verwalten | Status ändern: Bestellt → Zubereiten → Geliefert |
| Service-Anfragen | Kellner-Rufe bearbeiten |
| Zahlungen bestätigen | Gast hat bezahlt → Bestätigen |
| Session schließen | Gast vom System entfernen |

### 🍺 Kunde (Gast)

| Funktion | Beschreibung |
|----------|-------------|
| QR-Code scannen | Bierdeckel scannen → Session starten |
| Menü ansehen | Getränke und Speisen nach Kategorie |
| Bestellen | Warenkorb → Bestellung aufgeben |
| Bestellhistorie | Status der Bestellungen sehen |
| Service rufen | Kellner, Servietten, Sonstiges |
| Bezahlen | Einzeln oder für Gruppe |
| Zusammen trinken | Gruppe bilden mit anderen Gästen |
| Trinkspiel | Spiel erstellen/beitreten |

---

## Funktionslogik im Detail

### 1. QR-Code Scan & Session

```
Gast scannt QR-Code auf Bierdeckel
     │
     ▼
URL: /r/{restaurant_id}/bd/{bierdeckel_id}
     │
     ▼
Backend prüft: Gibt es schon eine aktive Session?
     │
     ├── JA → Bestehende Session zurückgeben
     │
     └── NEIN → Neue Session erstellen
                 ├── session_id generieren
                 ├── bierdeckel_id verknüpfen
                 ├── table_id verknüpfen
                 └── Gast wird zum Menü weitergeleitet
```

### 2. Bestell-Ablauf

```
Gast (Kunden-App)                    Kellner (Dashboard)
     │                                      │
     │  Getränke zum Warenkorb               │
     │  hinzufügen                           │
     │                                      │
     │  "Jetzt bestellen" klicken            │
     │ ──────────────────────────────────► Bestellung erscheint
     │                                      │
     │  Status: ⏳ Bestellt                  │ Klick: "👨‍🍳 Zubereiten"
     │                                      │
     │  Status: 👨‍🍳 In Zubereitung          │ Klick: "✅ Geliefert"
     │                                      │
     │  Status: ✅ Geliefert                 │
```

### 3. Bezahl-Ablauf

```
┌─────────────────────────────────────────────┐
│              Bezahlen                        │
│                                              │
│  📋 Deine Bestellungen:                     │
│  ─────────────────────                       │
│  2x Weißbier            9.00 €              │
│  1x Cola                2.80 €              │
│  ─────────────────────                       │
│  Gesamt:               11.80 €              │
│  Bereits bezahlt:       0.00 €              │
│  Noch offen:           11.80 €              │
│                                              │
│  [🔔 Kellner rufen]                         │
│  [💳 Jetzt bezahlen]                        │
│                                              │
│  Nach Bezahlung:                             │
│  [👋 Tisch verlassen] → Session wird beendet │
└─────────────────────────────────────────────┘
```

**Kellner-Bezahlung:**
```
Gast klickt "Kellner rufen"
     │
     ▼
Kellner sieht Zahlungswunsch im Dashboard
     │
     ▼
Gast bezahlt bar/Karte beim Kellner
     │
     ▼
Kellner klickt "✅ Als bezahlt bestätigen"
```

### 4. Zusammen trinken – Komplett-Logik

```
SCHRITT 1: Bereitschaft signalisieren
─────────────────────────────────────
Gast B drückt "🍺 Bereit zum Trinken?"
     → Status: drink_ready = true
     → Gast B erscheint in der "Bereit"-Liste


SCHRITT 2: Einladung senden
────────────────────────────
Gast A öffnet "Zusammen trinken"
     → Sieht Liste: "Tisch 7 - bereit"
     → Klickt "Einladen"
     → Einladung wird an Gast B gesendet
     → Automatisch: Gruppe wird erstellt (Invite-Code: T1-A3X9)


SCHRITT 3: Einladung annehmen
─────────────────────────────
Gast B sieht: "Tisch 1 möchte mit dir trinken!"
     → Klickt "✅ Annehmen"
     → Gast B wird der Gruppe hinzugefügt
     → Beide: drink_ready wird zurückgesetzt
     → "Bereit"-Liste wird geleert


SCHRITT 4: In der Gruppe
─────────────────────────
Beide sehen:
┌──────────────────────────┐
│  👥 Deine Gruppe          │
│  Code: T1-A3X9            │
│                            │
│  🪑 Tisch 1 (Du)         │
│  🪑 Tisch 7               │
│                            │
│  [🚪 Gruppe verlassen]    │
└──────────────────────────┘


SCHRITT 5: Gruppen-Bezahlung
─────────────────────────────
Unter "Bezahlen" erscheint:
  [Meine Rechnung] [Gruppen-Rechnung]

Gruppen-Rechnung zeigt ALLE Bestellungen:
  T1: 2x Weißbier    9.00 €
  T7: 1x Helles      3.90 €
  ─────────────────────────
  Gesamt:            12.90 €

  [💳 Für alle bezahlen (12.90 €)]


ALTERNATIVE: Code teilen
─────────────────────────
Statt Einladung kann man auch den Code teilen:
Gast A: "Hey, mein Code ist T1-A3X9"
Gast B: Gibt Code ein → tritt direkt bei
```

### 5. Trinkspiel – Komplett-Logik

```
VORAUSSETZUNG:
─────────────
Alle Spieler müssen ein geliefertes Getränk haben!
(Bestellt + Kellner hat auf "Geliefert" geklickt)


SCHRITT 1: Spiel erstellen
───────────────────────────
Gast A öffnet "🎮 Trinkspiel"
     → Wählt Getränk aus (z.B. Weißbier)
     → Klickt "🎮 Spiel erstellen"
     → Spiel erscheint in der Liste aller offenen Spiele
     → Status: ⏳ Wartet auf Mitspieler


SCHRITT 2: Beitritt anfragen
─────────────────────────────
Gast B öffnet "🎮 Trinkspiel"
     → Sieht: "Tisch 1 - 1 Spieler"
     → Klickt "Beitreten"
     → Beitrittsanfrage wird gesendet


SCHRITT 3: Genehmigung
───────────────────────
Gast A (Ersteller) sieht Anfrage:
┌─────────────────────────────┐
│  📩 Beitrittsanfragen        │
│                               │
│  🪑 Tisch 7  [✅] [❌]      │
│  🪑 Tisch 3  [✅] [❌]      │
│                               │
│  [🏁 Spiel starten (3 Spieler)]│
└─────────────────────────────┘
     → Gast A genehmigt Spieler
     → Mindestens 2 genehmigte Spieler nötig


SCHRITT 4: Spiel starten
─────────────────────────
Gast A klickt "🏁 Spiel starten"
     → Alle sehen: Status "🏁 Läuft!"
     → Jeder hat Button: "🍺 Fertig getrunken!"


SCHRITT 5: Wer zuletzt trinkt, verliert!
──────────────────────────────────────────
Gast A trinkt aus → klickt "🍺 Fertig getrunken!" → ✅ Fertig
Gast C trinkt aus → klickt "🍺 Fertig getrunken!" → ✅ Fertig
Gast B trinkt als Letzter aus → klickt → 😅 VERLIERER!


SCHRITT 6: Abrechnung
──────────────────────
Verlierer zahlt die Getränke der Gewinner!

VORHER:
  Gast A: Weißbier 4.50 €
  Gast B: Weißbier 4.50 €
  Gast C: Weißbier 4.50 €

NACHHER (Gast B verliert):
  Gast A: 0.00 € (Getränk entfernt)
  Gast B: 13.50 € (eigenes + A's + C's Getränk)
  Gast C: 0.00 € (Getränk entfernt)
```

### 6. Service rufen

```
Gast klickt "🔔 Service" Button
     │
     ▼
Auswahl:
  [🧑‍🍳 Kellner rufen]
  [🧻 Servietten]
  [❓ Sonstiges]
     │
     ▼
Kellner sieht im Dashboard:
┌────────────────────────────┐
│  🔔 Service (2)            │
│                             │
│  🪑 Tisch 1 - Kellner      │
│  [🏃 In Bearbeitung]       │
│                             │
│  🪑 Tisch 7 - Servietten   │
│  [🏃 In Bearbeitung]       │
└────────────────────────────┘
     │
     ▼
Kellner klickt "✅ Erledigt" → Anfrage verschwindet
```

### 7. Bierdeckel Füllstand (MQTT)

```
Bierdeckel (Hardware)
     │
     │ Gewichtssensor misst Glasgewicht
     │
     ▼ MQTT
MQTT Broker
     │
     │ HTTP POST /bierdeckel/update
     │ Body: { bierdeckel_id: "...", weight: 350 }
     │
     ▼
Backend berechnet Status:
  < 50g   → "empty"  (🔴 Leer)
  < 200g  → "low"    (🟠 Wenig)
  < 350g  → "half"   (🟡 Halb)
  ≥ 350g  → "full"   (🟢 Voll)
     │
     ▼
Dashboard zeigt:
┌─────────────────────────┐
│  🍺 Füllstand            │
│                           │
│  Tisch 1                  │
│  BD-001: 🟢 Voll (420g) │
│  BD-002: 🟠 Wenig (120g)│
│                           │
│  Tisch 2                  │
│  BD-003: 🔴 Leer (30g)  │
└─────────────────────────┘
```

### 8. Session schließen

```
Zwei Möglichkeiten:

1. KUNDE schließt selbst:
   Bezahlen → "👋 Tisch verlassen"
   → Session wird geschlossen
   → Kunde wird ausgeloggt

2. KELLNER schließt:
   Dashboard → Tisch → "❌ Session schließen"
   → Session wird geschlossen
   → Kunde bekommt Meldung: "Session wurde beendet"
   → Kunde wird automatisch ausgeloggt
```

---

## Technologie-Stack

| Komponente | Technologie |
|-----------|-------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy |
| Datenbank | SQLite |
| Auth | JWT Token, bcrypt |
| Frontend Kunden | React, axios, react-router-dom |
| Frontend Dashboard | React (gleiche App, getrennte Struktur) |
| QR-Code | qrcode[pil] Library |
| Bierdeckel-Sensor | MQTT (externe Komponente) |

---

## API-Endpunkte Übersicht

### Restaurant & Auth
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /auth/register-owner | Owner + Restaurant erstellen |
| POST | /auth/register-staff/{id} | Mitarbeiter anlegen |
| POST | /auth/login | Login → JWT Token |

### Tische & Bierdeckel
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /restaurant/{id}/table | Tisch erstellen |
| GET | /restaurant/{id}/tables | Alle Tische |
| POST | /table/{id}/bierdeckel | Bierdeckel erstellen |
| GET | /bierdeckel/{id}/qr | QR-Code als Bild |

### Session
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /r/{rid}/bd/{bid}/scan | QR-Scan → Session |
| PUT | /session/{id}/close | Session beenden |

### Menü
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /restaurant/{id}/menu | Menü-Item erstellen |
| GET | /restaurant/{id}/menu | Menü abrufen |
| PUT | /menu/{id} | Item bearbeiten |
| DELETE | /menu/{id} | Item löschen |

### Bestellungen
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /session/{id}/order | Bestellung aufgeben |
| GET | /session/{id}/orders | Bestellhistorie |
| PUT | /order/{id}/status/{s} | Status ändern |
| GET | /restaurant/{id}/orders | Alle offenen Bestellungen |

### Bezahlung
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| GET | /session/{id}/bill | Rechnung mit Artikeln |
| POST | /session/{id}/pay | Einzelzahlung |
| POST | /session/{id}/pay-group | Für Gruppe bezahlen |
| POST | /session/{id}/payment-request | Kellner rufen |
| PUT | /payment/{id}/confirm | Kellner bestätigt |
| GET | /session/{id}/group-bill | Gruppen-Rechnung |

### Zusammen trinken
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| PUT | /session/{id}/drink-ready | Bereit an/aus |
| GET | /restaurant/{id}/drink-ready | Wer ist bereit? |
| POST | /session/{id}/create-group | Gruppe erstellen |
| POST | /session/{id}/join/{code} | Mit Code beitreten |
| POST | /session/{id}/invite/{sid} | Einladung senden |
| PUT | /invitation/{id}/accept | Einladung annehmen |
| PUT | /invitation/{id}/decline | Einladung ablehnen |
| GET | /group/{id} | Gruppe ansehen |
| PUT | /session/{id}/leave-group | Gruppe verlassen |

### Trinkspiel
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /session/{id}/game/create | Spiel erstellen |
| GET | /restaurant/{id}/games | Offene Spiele |
| POST | /game/{id}/request-join/{sid} | Beitritt anfragen |
| GET | /game/{id}/requests | Anfragen sehen |
| PUT | /game/{id}/approve/{pid} | Spieler genehmigen |
| PUT | /game/{id}/start | Spiel starten |
| POST | /game/{id}/finish | Fertig getrunken |
| GET | /game/{id} | Spielstatus |

### Service & Dashboard
| Methode | Endpunkt | Beschreibung |
|---------|----------|-------------|
| POST | /session/{id}/service-request | Service rufen |
| GET | /restaurant/{id}/service-requests | Offene Anfragen |
| PUT | /service-request/{id}/status/{s} | Status ändern |
| GET | /restaurant/{id}/dashboard | Dashboard Übersicht |
| POST | /bierdeckel/update | Füllstand (MQTT Bridge) |
| GET | /restaurant/{id}/bierdeckel | Alle Füllstände |

---

## Projektstruktur

```
bierdeckel/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── database/
│   │   └── db.py
│   ├── models/
│   │   ├── restaurant.py
│   │   ├── user.py
│   │   ├── table.py
│   │   ├── bierdeckel.py
│   │   ├── session.py
│   │   ├── menu.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   ├── drink.py
│   │   └── game.py
│   └── routes/
│       ├── restaurant.py
│       ├── auth.py
│       ├── table.py
│       ├── bierdeckel.py
│       ├── session.py
│       ├── menu.py
│       ├── order.py
│       ├── payment.py
│       ├── drink.py
│       ├── game.py
│       └── service.py
│
└── frontend/
    └── src/
        ├── api.js
        ├── App.js
        ├── index.js
        ├── customer/
        │   ├── pages/
        │   │   ├── Home.js
        │   │   ├── Menu.js
        │   │   ├── Cart.js
        │   │   ├── OrderHistory.js
        │   │   ├── Payment.js
        │   │   ├── DrinkTogether.js
        │   │   └── Game.js
        │   └── components/
        │       └── Navbar.js
        └── dashboard/
            ├── pages/
            │   ├── Login.js
            │   ├── Dashboard.js
            │   ├── MenuManager.js
            │   ├── TableManager.js
            │   └── StaffManager.js
            └── components/
                └── DashboardNav.js
```

---

## GitHub

Repository: https://github.com/Alhoush/bierdeckel
