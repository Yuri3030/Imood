from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Reminder
from app.schemas import ReminderCreate, ReminderResponse

router = APIRouter(prefix="/users/{user_id}/reminders", tags=["reminders"])

@router.post("", response_model=ReminderResponse, status_code=201)
def create_reminder(user_id: int, payload: ReminderCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    reminder = Reminder(
        user_id=user_id,
        message=payload.message,
        due_at=payload.due_at,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder

@router.get("", response_model=List[ReminderResponse])
def list_user_reminders(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return (
        db.query(Reminder)
        .filter(Reminder.user_id == user_id)
        .order_by(Reminder.due_at.asc())
        .all()
    )

@router.patch("/{reminder_id}/done", response_model=ReminderResponse)
def toggle_done(user_id: int, reminder_id: int, done: bool = True, db: Session = Depends(get_db)):
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == user_id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Lembrete não encontrado")
    reminder.done = done
    db.commit()
    db.refresh(reminder)
    return reminder

@router.delete("/{reminder_id}", status_code=200)
def delete_reminder(user_id: int, reminder_id: int, db: Session = Depends(get_db)):
    reminder = (
        db.query(Reminder)
        .filter(Reminder.id == reminder_id, Reminder.user_id == user_id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=404, detail="Lembrete não encontrado")
    db.delete(reminder)
    db.commit()
    return {"message": "Lembrete deletado com sucesso"}
