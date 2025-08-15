from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pessoa, CheckIn
from app.schemas import CheckInCreate, CheckInResponse

router = APIRouter(prefix="/pessoas/{pessoa_id}/check_ins", tags=["check_ins"])

@router.post("", response_model=CheckInResponse, status_code=201)
def create_checkin(pessoa_id: int, payload: CheckInCreate, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    entry = CheckIn(
        pessoa_id=pessoa_id,
        score=payload.score,
        checkin_type=payload.checkin_type,
        comment=payload.comment,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@router.get("", response_model=List[CheckInResponse])
def list_checkins(pessoa_id: int, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    return (
        db.query(CheckIn)
        .filter(CheckIn.pessoa_id == pessoa_id)
        .order_by(CheckIn.created_at.desc())
        .all()
    )
