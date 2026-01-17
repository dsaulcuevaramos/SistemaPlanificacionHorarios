from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.core.database import engine
from app.models.base import Base
from app import models
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log para que veas en consola que está intentando crear las tablas
    print("Iniciando creación de tablas...")
    async with engine.begin() as conn:
        # run_sync es obligatorio para motores asíncronos
        await conn.run_sync(Base.metadata.create_all)
    print("Tablas creadas con éxito.")
    yield

# 1. Inicializar la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

"""
origins = ["http://localhost",     # Para pruebas locales simples
    "http://localhost:5173",      # Puerto por defecto de Vue 3 (Vite)
    "http://localhost:8080",      # Puerto común de Vue 2 / Webpack
    "http://127.0.0.1:5173",      # Variante de localhost con IP
    "http://5.161.126.165",       # <--- IMPORTANTE: La IP pública de tu servidor (Si sirves el front ahí)
    "http://5.161.126.165:80",]
"""
origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:5173",
    "http://5.161.126.165",      # Tu IP
    "http://5.161.126.165:8080", # Tu IP con puerto Frontend
    "*"                          # Comodín (Úsalo solo si estás desesperado)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    return {"mensaje": "Sistema de Horarios UNU - API Activa"}

