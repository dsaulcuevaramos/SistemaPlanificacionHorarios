from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.core.database import get_db
from app.crud.crud_turno import turno as crud_turno
from app.schemas.turno import TurnoCreate, TurnoResponse 

from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.models.turno import Turno
from app.models.plan_version import PlanVersion
from app.models.plan_estudio import PlanEstudio
from app.crud.crud_bloque import bloque as crud_bloque
from app.schemas.turno import TurnoCreate, TurnoResponse, BloqueHorarioCreate, BloqueHorarioResponse, TurnoUpdate


router = APIRouter()

# --- RUTAS DE TURNOS ---

@router.get("/", response_model=List[TurnoResponse])
async def read_turnos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los turnos de la escuela del usuario actual."""
    if not current_user.id_escuela:
        return []
    return await crud_turno.get_multi_by_escuela(db, id_escuela=current_user.id_escuela)

@router.post("/", response_model=TurnoResponse)
async def create_turno(
    turno_in: TurnoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea un turno para la escuela del usuario."""
    if not current_user.id_escuela:
        raise HTTPException(status_code=400, detail="El usuario no pertenece a una escuela.")

    if turno_in.hora_inicio >= turno_in.hora_fin:
        raise HTTPException(status_code=400, detail="Hora inicio debe ser menor a hora fin.")

    # Asignamos la escuela automáticamente
    turno_in.id_escuela = current_user.id_escuela
    return await crud_turno.create(db, obj_in=turno_in)


@router.put("/{turno_id}", response_model=TurnoResponse)
async def update_turno(
    turno_id: int,
    turno_in: TurnoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    turno_obj = await crud_turno.get(db, id=turno_id)
    if not turno_obj:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
        
    if turno_obj.id_escuela != current_user.id_escuela:
        raise HTTPException(status_code=403, detail="No tienes permiso sobre este turno.")

    return await crud_turno.update(db, db_obj=turno_obj, obj_in=turno_in)




@router.delete("/{turno_id}", tags=["Turnos"])
async def delete_turno(
    turno_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina un turno. Valida permisos sobre la escuela.
    """
    # 1. Verificar si el turno existe y obtener su contexto (Plan -> Escuela)
    stmt = (
        select(Turno, PlanEstudio.id_escuela)
        .join(PlanVersion, Turno.version_id == PlanVersion.id)
        .join(PlanEstudio, PlanVersion.id_plan_estudio == PlanEstudio.id)
        .where(Turno.id == turno_id)
    )
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        raise HTTPException(status_code=404, detail="Turno no encontrado.")
    
    turno_obj, escuela_id = row

    # 2. VALIDACIÓN DE PERMISOS
    if current_user.id_escuela and escuela_id != current_user.id_escuela:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para eliminar este turno (pertenece a otra escuela)."
        )

    # 3. Eliminar
    await crud_turno.remove(db, id=turno_id)
    return {"message": "Turno eliminado correctamente"}

# --- RUTAS DE BLOQUES HORARIOS ---

@router.post("/bloques/", response_model=BloqueHorarioResponse)
async def create_bloque(
    bloque_in: BloqueHorarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """Agrega un bloque horario a un turno existente."""
    # Validar que el turno exista
    turno_obj = await crud_turno.get(db, id=bloque_in.id_turno)
    if not turno_obj:
        raise HTTPException(status_code=404, detail="El turno especificado no existe.")
        
    return await crud_bloque.create(db, obj_in=bloque_in)
