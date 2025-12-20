from fastapi import APIRouter
from app.api.endpoints import auth, catalogo, usuario                       #esto es todo lo que tiene que ver con auth
from app.api.endpoints import plan_estudio,plan_version,curso               #esto es todo lo que tiene que ver con cursos
from app.api.endpoints import docente                   #esto es todo lo que tiene que ver con docentes
from app.api.endpoints import aula,turno 

from app.api.endpoints import periodo
from app.api.endpoints import curso_aperturado
from app.api.endpoints import contratos

from app.api.endpoints import horarios
from app.api.endpoints import gestion_horarios
api_router = APIRouter()

#PLANIFICACION

# Mod uath
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
api_router.include_router(catalogo.router, prefix="/catalogo", tags=["Catálogos"])
api_router.include_router(usuario.router, prefix="/usuarios", tags=["Usuarios"]) 

# Mod cursos
api_router.include_router(plan_estudio.router, prefix="/planes", tags=["Planes de Estudio"])
api_router.include_router(plan_version.router, prefix="/versiones", tags=["Planes de Estudio"])
api_router.include_router(curso.router, prefix="/cursos", tags=["Cursos"])

# Mod docentes
api_router.include_router(docente.router, prefix="/docentes", tags=["Docentes"])

# mod Infraestructura
api_router.include_router(aula.router, prefix="/aulas", tags=["Infraestructura"])
api_router.include_router(turno.router, prefix="/turnos", tags=["Infraestructura"])


#PROGRAMACION
api_router.include_router(periodo.router, prefix="/periodos", tags=["Programación"])
api_router.include_router(curso_aperturado.router, prefix="/aperturas", tags=["Apertura Académica"])
api_router.include_router(contratos.router, prefix="/contratos", tags=["Contratos Docentes"])

api_router.include_router(horarios.router,  prefix="/horarios", tags=["Horarios"])
api_router.include_router(gestion_horarios.router,  prefix="/gestion_horarios", tags=["Horarios"])
# api_router.include_router(escuela.router, prefix="/escuelas", tags=["Escuelas"])