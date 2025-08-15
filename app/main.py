# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.settings import get_settings

from app.routers.pessoas import router as pessoas_router
from app.routers.check_ins import router as check_ins_router
from app.routers.lembretes import router as lembretes_router
from app.routers.contatos_emergencia import router as contatos_emergencia_router
from app.routers.contatos_emergencia import ensure_default_emergency_contacts

settings = get_settings()
app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "🚀 FastAPI + PostgreSQL funcionando! (sem autenticação)"}

# registra novos routers
app.include_router(pessoas_router)
app.include_router(check_ins_router)
app.include_router(lembretes_router)
app.include_router(contatos_emergencia_router)

# seed dos contatos padrão
@app.on_event("startup")
def on_startup():
    ensure_default_emergency_contacts()
