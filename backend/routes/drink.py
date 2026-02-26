from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from models.session import TableSession
from models.table import Table
from models.drink import DrinkGroup, Invitation
import random
import string

router = APIRouter()

def generate_invite_code(table_number):
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"T{table_number}-{random_part}"

# Bereit zum Trinken
@router.put("/session/{session_id}/drink-ready")
def toggle_drink_ready(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    session.drink_ready = not session.drink_ready
    db.commit()

    return {
        "session_id": session_id,
        "drink_ready": session.drink_ready,
        "message": "Bereit zum Trinken!" if session.drink_ready else "Nicht mehr bereit"
    }

# Wer ist bereit?
@router.get("/restaurant/{restaurant_id}/drink-ready")
def get_drink_ready(restaurant_id: str, db: Session = Depends(get_db)):
    sessions = db.query(TableSession).filter(
        TableSession.restaurant_id == restaurant_id,
        TableSession.is_active == True,
        TableSession.drink_ready == True
    ).all()

    result = []
    for s in sessions:
        table = db.query(Table).filter(Table.id == s.table_id).first()
        result.append({
            "session_id": s.id,
            "table_number": table.table_number if table else None,
            "created_at": str(s.created_at)
        })
    return result

# Gruppe erstellen
@router.post("/session/{session_id}/create-group")
def create_group(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    if session.group_id:
        raise HTTPException(status_code=400, detail="Du bist bereits in einer Gruppe")

    table = db.query(Table).filter(Table.id == session.table_id).first()
    code = generate_invite_code(table.table_number if table else 0)

    new_group = DrinkGroup(
        invite_code=code,
        restaurant_id=session.restaurant_id
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    session.group_id = new_group.id
    db.commit()

    return {
        "group_id": new_group.id,
        "invite_code": new_group.invite_code,
        "message": f"Gruppe erstellt! Teile den Code: {code}"
    }

# Mit Code beitreten
@router.post("/session/{session_id}/join/{invite_code}")
def join_group(session_id: str, invite_code: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")

    if session.group_id:
        raise HTTPException(status_code=400, detail="Du bist bereits in einer Gruppe")

    group = db.query(DrinkGroup).filter(
        DrinkGroup.invite_code == invite_code,
        DrinkGroup.status == "active"
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Ungültiger Code")

    session.group_id = group.id
    db.commit()

    return {
        "message": "Gruppe beigetreten!",
        "group_id": group.id,
        "invite_code": invite_code
    }

# Einladung senden
@router.post("/session/{session_id}/invite/{target_session_id}")
def send_invitation(session_id: str, target_session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id,
        TableSession.is_active == True
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Eigene Session nicht gefunden")

    target = db.query(TableSession).filter(
        TableSession.id == target_session_id,
        TableSession.is_active == True,
        TableSession.drink_ready == True
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Ziel-Session nicht gefunden oder nicht bereit")

    if not session.group_id:
        table = db.query(Table).filter(Table.id == session.table_id).first()
        code = generate_invite_code(table.table_number if table else 0)
        new_group = DrinkGroup(
            invite_code=code,
            restaurant_id=session.restaurant_id
        )
        db.add(new_group)
        db.commit()
        db.refresh(new_group)
        session.group_id = new_group.id
        db.commit()

    invitation = Invitation(
        from_session_id=session_id,
        to_session_id=target_session_id,
        group_id=session.group_id
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)

    from_table = db.query(Table).filter(Table.id == session.table_id).first()

    return {
        "message": "Einladung gesendet!",
        "invitation_id": invitation.id,
        "from_table": from_table.table_number if from_table else None,
        "to_session": target_session_id
    }

# Meine Einladungen sehen
@router.get("/session/{session_id}/invitations")
def get_invitations(session_id: str, db: Session = Depends(get_db)):
    invitations = db.query(Invitation).filter(
        Invitation.to_session_id == session_id,
        Invitation.status == "pending"
    ).all()

    result = []
    for inv in invitations:
        from_session = db.query(TableSession).filter(TableSession.id == inv.from_session_id).first()
        from_table = db.query(Table).filter(Table.id == from_session.table_id).first()
        result.append({
            "invitation_id": inv.id,
            "from_table": from_table.table_number if from_table else None,
            "group_id": inv.group_id,
            "created_at": str(inv.created_at)
        })
    return result

# Einladung akzeptieren
@router.put("/invitation/{invitation_id}/accept")
def accept_invitation(invitation_id: str, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Einladung nicht gefunden")
    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail="Einladung bereits beantwortet")

    invitation.status = "accepted"

    session = db.query(TableSession).filter(TableSession.id == invitation.to_session_id).first()
    session.group_id = invitation.group_id
    db.commit()

    return {
        "message": "Einladung akzeptiert! Du bist jetzt in der Gruppe.",
        "group_id": invitation.group_id
    }

# Einladung ablehnen
@router.put("/invitation/{invitation_id}/decline")
def decline_invitation(invitation_id: str, db: Session = Depends(get_db)):
    invitation = db.query(Invitation).filter(Invitation.id == invitation_id).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Einladung nicht gefunden")
    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail="Einladung bereits beantwortet")

    invitation.status = "declined"
    db.commit()

    return {"message": "Einladung abgelehnt"}

# Gruppe ansehen
@router.get("/group/{group_id}")
def get_group(group_id: str, db: Session = Depends(get_db)):
    group = db.query(DrinkGroup).filter(DrinkGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")

    members = db.query(TableSession).filter(
        TableSession.group_id == group_id,
        TableSession.is_active == True
    ).all()

    member_list = []
    for m in members:
        table = db.query(Table).filter(Table.id == m.table_id).first()
        member_list.append({
            "session_id": m.id,
            "table_number": table.table_number if table else None
        })

    return {
        "group_id": group.id,
        "invite_code": group.invite_code,
        "status": group.status,
        "members": member_list
    }

# Gruppe verlassen
@router.put("/session/{session_id}/leave-group")
def leave_group(session_id: str, db: Session = Depends(get_db)):
    session = db.query(TableSession).filter(
        TableSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session nicht gefunden")
    if not session.group_id:
        raise HTTPException(status_code=400, detail="Du bist in keiner Gruppe")

    group_id = session.group_id
    session.group_id = None
    db.commit()

    remaining = db.query(TableSession).filter(
        TableSession.group_id == group_id,
        TableSession.is_active == True
    ).count()

    if remaining == 0:
        group = db.query(DrinkGroup).filter(DrinkGroup.id == group_id).first()
        if group:
            group.status = "closed"
            db.commit()

    return {"message": "Gruppe verlassen"}