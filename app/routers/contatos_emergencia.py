from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import ContatoEmergencia, Pessoa
from app.schemas import ContatoEmergenciaCreate, ContatoEmergenciaResponse

router = APIRouter(prefix="/pessoas/{pessoa_id}/contatos_emergencia", tags=["contatos_emergencia"])

DEFAULT_BR_CONTACTS = [
    {"name": "Polícia Militar", "phone": "190", "category": "seguranca"},
    {"name": "SAMU (Ambulância)", "phone": "192", "category": "saude"},
    {"name": "Bombeiros", "phone": "193", "category": "seguranca"},
    {"name": "Defesa Civil", "phone": "199", "category": "defesa"},
    {"name": "Delegacia da Mulher", "phone": "180", "category": "direitos"},
    {"name": "Disque Denúncia", "phone": "181", "category": "seguranca"},
    {"name": "CVV - Prevenção ao Suicídio", "phone": "188", "category": "saude"},
    {"name": "PRF - Polícia Rodoviária Federal", "phone": "191", "category": "seguranca"},
    {"name": "Disque Saúde (SUS)", "phone": "136", "category": "saude"},
]

def ensure_default_emergency_contacts():
    db: Session = SessionLocal()
    try:
        exists = db.query(ContatoEmergencia).filter(
            ContatoEmergencia.is_default.is_(True),
            ContatoEmergencia.deleted_at.is_(None)
        ).first()
        if exists:
            return
        for c in DEFAULT_BR_CONTACTS:
            db.add(ContatoEmergencia(
                pessoa_id=None,
                name=c["name"],
                phone=c["phone"],
                category=c.get("category"),
                is_default=True
            ))
        db.commit()
    finally:
        db.close()

@router.get("", response_model=List[ContatoEmergenciaResponse])
def list_all(pessoa_id: int, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    return (
        db.query(ContatoEmergencia)
        .filter(ContatoEmergencia.deleted_at.is_(None))
        .filter((ContatoEmergencia.is_default.is_(True)) | (ContatoEmergencia.pessoa_id == pessoa_id))
        .order_by(ContatoEmergencia.is_default.desc(), ContatoEmergencia.name.asc())
        .all()
    )

@router.post("", response_model=ContatoEmergenciaResponse, status_code=201)
def create_contact(pessoa_id: int, payload: ContatoEmergenciaCreate, db: Session = Depends(get_db)):
    p = db.query(Pessoa).get(pessoa_id)
    if not p:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    ec = ContatoEmergencia(
        pessoa_id=pessoa_id,
        name=payload.name,
        phone=payload.phone,
        category=payload.category,
        is_default=False
    )
    db.add(ec)
    db.commit()
    db.refresh(ec)
    return ec

@router.delete("/{contact_id}", status_code=200)
def delete_contact(pessoa_id: int, contact_id: int, db: Session = Depends(get_db)):
    ec = db.query(ContatoEmergencia).filter(ContatoEmergencia.id == contact_id).first()
    if not ec or ec.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    if ec.is_default:
        raise HTTPException(status_code=403, detail="Contato padrão não pode ser excluído por esta rota")

    if ec.pessoa_id != pessoa_id:
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este contato")

    ec.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Contato excluído com sucesso (soft delete)."}
