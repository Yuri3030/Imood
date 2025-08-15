# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import get_settings

# 🔽 importe o "router" diretamente de cada arquivo
from app.routers.users import router as users_router
from app.routers.moods import router as moods_router
from app.routers.reminders import router as reminders_router
from app.routers.emergency_contacts import router as emergency_contacts_router

from app.startup import run_startup_tasks

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

# 🔽 registre os routers importados acima
app.include_router(users_router)
app.include_router(moods_router)
app.include_router(reminders_router)
app.include_router(emergency_contacts_router)

@app.on_event("startup")
def on_startup():
    run_startup_tasks()
