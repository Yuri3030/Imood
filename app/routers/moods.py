from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Mood
from app.schemas import MoodCreate, MoodResponse

router = APIRouter(prefix="/users/{user_id}/moods", tags=["moods"])

@router.post("", response_model=MoodResponse, status_code=201)
def create_mood(user_id: int, payload: MoodCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    entry = Mood(
        user_id=user_id,
        score=payload.score,
        mood_type=payload.mood_type,
        comment=payload.comment,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("", response_model=List[MoodResponse])
def list_user_moods(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return (
        db.query(Mood)
        .filter(Mood.user_id == user_id)
        .order_by(Mood.created_at.desc())
        .all()
    )
