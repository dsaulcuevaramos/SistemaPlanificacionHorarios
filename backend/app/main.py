from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router
from app.core.database import engine
from app.models import Base
from contextlib import asynccontextmanager

# 1. Inicializar la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
"""
app = FastAPI(
    title="Sistema de Gestión de Horarios UNU",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs"
)

    ["http://localhost",           # Para pruebas locales simples
    "http://localhost:5173",      # Puerto por defecto de Vue 3 (Vite)
    "http://localhost:8080",      # Puerto común de Vue 2 / Webpack
    "http://127.0.0.1:5173",      # Variante de localhost con IP
    "http://5.161.126.165",       # <--- IMPORTANTE: La IP pública de tu servidor (Si sirves el front ahí)
    "http://5.161.126.165:80",]
"""

origins = ["*"]  # Por ahora permitimos todo para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    return {"mensaje": "Sistema de Horarios UNU - API Activa"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔄 Iniciando sistema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tablas listas.")
    yield
    print("🛑 Apagando...")