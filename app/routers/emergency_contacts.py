from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import EmergencyContact, User

from app.schemas import EmergencyContactCreate, EmergencyContactResponse

router = APIRouter(prefix="/users/{user_id}/emergency-contacts", tags=["emergency-contacts"])

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
        exists = db.query(EmergencyContact).filter(
            EmergencyContact.is_default.is_(True),
            EmergencyContact.deleted_at.is_(None)
        ).first()
        if exists:
            return
        for c in DEFAULT_BR_CONTACTS:
            db.add(EmergencyContact(
                user_id=None,
                name=c["name"],
                phone=c["phone"],
                category=c.get("category"),
                is_default=True
            ))
        db.commit()
    finally:
        db.close()

@router.get("", response_model=List[EmergencyContactResponse])
def list_all_contacts(user_id: int, db: Session = Depends(get_db)):
    """Lista contatos padrão + contatos do usuário informado."""
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    q = db.query(EmergencyContact).filter(EmergencyContact.deleted_at.is_(None)).filter(
        (EmergencyContact.is_default.is_(True)) | (EmergencyContact.user_id == user_id)
    ).order_by(EmergencyContact.is_default.desc(), EmergencyContact.name.asc())
    return q.all()

@router.post("", response_model=EmergencyContactResponse, status_code=201)
def create_contact(user_id: int, payload: EmergencyContactCreate, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    ec = EmergencyContact(
        user_id=user_id,
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
def delete_contact(user_id: int, contact_id: int, db: Session = Depends(get_db)):
    """Soft delete: só pode excluir contatos do próprio usuário; defaults ninguém exclui aqui."""
    ec = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()
    if not ec or ec.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Contato não encontrado")

    if ec.is_default:
        raise HTTPException(status_code=403, detail="Contato padrão não pode ser excluído por esta rota")

    if ec.user_id != user_id:
        raise HTTPException(status_code=403, detail="Sem permissão para excluir este contato")

    ec.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Contato excluído com sucesso (soft delete)."}

