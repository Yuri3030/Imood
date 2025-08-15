from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pessoa, Lembrete
from app.schemas import LembreteCreate, LembreteResponse

router = APIRouter(prefix="/pessoas/{pessoa_id}/lembretes", tags=["lembretes"])

@router.post("", response_model=LembreteResponse, status_code=201)
def create_lembrete(pessoa_id: int, payload: LembreteCreate, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    r = Lembrete(pessoa_id=pessoa_id, message=payload.message, due_at=payload.due_at)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get("", response_model=List[LembreteResponse])
def list_lembretes(pessoa_id: int, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    return (
        db.query(Lembrete)
        .filter(Lembrete.pessoa_id == pessoa_id)
        .order_by(Lembrete.due_at.asc())
        .all()
    )

@router.patch("/{lembrete_id}/done", response_model=LembreteResponse)
def toggle_done(pessoa_id: int, lembrete_id: int, done: bool = True, db: Session = Depends(get_db)):
    r = db.query(Lembrete).filter(Lembrete.id == lembrete_id, Lembrete.pessoa_id == pessoa_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Lembrete não encontrado")
    r.done = done
    db.commit()
    db.refresh(r)
    return r

@router.delete("/{lembrete_id}", status_code=200)
def delete_lembrete(pessoa_id: int, lembrete_id: int, db: Session = Depends(get_db)):
    r = db.query(Lembrete).filter(Lembrete.id == lembrete_id, Lembrete.pessoa_id == pessoa_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Lembrete não encontrado")
    db.delete(r)
    db.commit()
    return {"message": "Lembrete deletado com sucesso"}
