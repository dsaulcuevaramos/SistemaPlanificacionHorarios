"""# app/api/v1/api.py
from fastapi import APIRouter
from app.api.v1.endpoints import auth 
from app.api.v1.endpoints import docentes # <-- AÑADIDO
from app.api.v1.endpoints import requisitos # <-- AÑADIDO
from app.api.v1.endpoints import malla # <-- AÑADIDO
# from app.api.v1.endpoints import cursos # Lo agregarás después

# Este es el router principal para la versión 1 de tu API
api_router = APIRouter()

# 1. Incluye el router de autenticación
# Prefijo: /auth
# La ruta final será: /api/v1/auth/login
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(docentes.router, prefix="/docentes") # <-- Incluido
api_router.include_router(requisitos.router, prefix="/requisitos") # <-- Incluido
api_router.include_router(malla.router, prefix="/malla") # <-- Incluido
# api_router.include_router(docentes.router, prefix="/docentes")
# api_router.include_router(cursos.router, prefix="/cursos")

# app/api/v1/api.py (Actualizado)
"""