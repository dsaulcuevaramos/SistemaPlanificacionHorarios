# backend/app/core/errors.py
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.handler.exeptions import CruceHorarioError, DocenteNoDisponibleError, RecursoNoEncontradoError

# Configurar el Logger (Esto imprimirá en tu consola de servidor)
logger = logging.getLogger("uvicorn.error")

async def cruce_horario_handler(request: Request, exc: CruceHorarioError):
    # 1. LOG INTERNO (Para que tú sepas qué pasó)
    logger.warning(f"Intento de cruce de horario: {exc.mensaje} - Ruta: {request.url}")
    
    # 2. RESPUESTA AL CLIENTE (Vue.js)
    return JSONResponse(
        status_code=409, # Conflict
        content={"error": "Conflicto de Horario", "detalle": exc.mensaje},
    )

async def docente_no_disponible_handler(request: Request, exc: DocenteNoDisponibleError):
    logger.error(f"Error de disponibilidad: {exc.mensaje}")
    return JSONResponse(
        status_code=400, # Bad Request
        content={"error": "Docente Ocupado", "detalle": exc.mensaje},
    )