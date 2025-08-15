from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pessoa
from app import models
from app.schemas import PessoaCreate, PessoaResponse

router = APIRouter(prefix="/pessoas", tags=["pessoas"])

@router.post("/", response_model=PessoaResponse, status_code=201)
def create_pessoa(payload: PessoaCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Pessoa).filter(models.Pessoa.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    nova = models.Pessoa(
        name=payload.name,
        email=payload.email,
        date_of_birth=payload.date_of_birth,
        is_active=True,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova

@router.get("/", response_model=List[PessoaResponse])
def list_pessoas(db: Session = Depends(get_db)):
    return db.query(models.Pessoa).all()

@router.get("/{pessoa_id}", response_model=PessoaResponse)
def get_pessoa(pessoa_id: int, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    return p

@router.delete("/", status_code=200)
def delete_pessoa(email: str, db: Session = Depends(get_db)):
    p = db.query(Pessoa).filter(Pessoa.email == email, Pessoa.deleted_at.is_(None)).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")
    p.deleted_at = datetime.utcnow()
    p.is_active = False
    db.commit()
    return {"message": "Pessoa marcada como excluída"}
