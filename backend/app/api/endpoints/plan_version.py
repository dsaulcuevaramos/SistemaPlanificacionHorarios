from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.core.database import get_db 
from app.api.deps import get_current_user

from app.models.usuario import Usuario
from app.models.plan_version import PlanVersion
from app.models.plan_estudio import PlanEstudio  # Importante para validar la relación

from app.crud.crud_plan_version import plan_version as crud_plan_version
from app.schemas.plan_version import PlanVersionCreate, PlanVersionResponse, PlanVersionUpdate

router = APIRouter()

@router.get("/", response_model=List[PlanVersionResponse], tags=["Planes de Estudio"])
async def read_plan_versions(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    id_plan_estudio: Optional[int] = None # Cambiado a id_plan para coincidir con el front
):
    """Lista versiones. Soporta filtro por id_plan."""
    if id_plan_estudio:
        # Query manual directa para filtrar
        stmt = select(PlanVersion).where(PlanVersion.id_plan_estudio == id_plan_estudio) 
        result = await db.execute(stmt)
        return result.scalars().all()
    else:
        return await crud_plan_version.get_multi(db, skip=skip, limit=limit)
    

@router.post("/", response_model=PlanVersionResponse, tags=["Planes de Estudio"])
async def create_plan_version(
    version_in: PlanVersionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Crea una nueva versión."""
    
    # 1. SEGURIDAD: Verificar que el plan padre pertenezca a la escuela del usuario
    if current_user.id_escuela is not None:
        stmt = select(PlanEstudio).where(PlanEstudio.id == version_in.id_plan_estudio)
        result = await db.execute(stmt)
        plan_padre = result.scalar_one_or_none()

        if not plan_padre:
             raise HTTPException(status_code=404, detail="El plan de estudio especificado no existe.")
        
        if plan_padre.id_escuela != current_user.id_escuela:
             raise HTTPException(status_code=403, detail="No puedes crear versiones para un plan de otra escuela.")

    try:
        new_version = await crud_plan_version.create(db, obj_in=version_in)
        return new_version
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad. Verifica el código de versión.",
        )
    
@router.put("/{version_id}", response_model=PlanVersionResponse, tags=["Planes de Estudio"])
async def update_plan_version(
    version_id: int,
    version_in: PlanVersionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Actualiza una versión existente (Datos o Estado)."""
    
    # 1. Obtener versión
    version = await crud_plan_version.get(db, id=version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Versión no encontrada.")

    # 2. SEGURIDAD: Verificar permisos a través del Plan Padre
    if current_user.id_escuela is not None:
        # Hacemos un JOIN para ver la escuela del plan padre de esta versión
        stmt = (
            select(PlanEstudio.id_escuela)
            .join(PlanVersion, PlanVersion.id_plan_estudio == PlanEstudio.id)
            .where(PlanVersion.id == version_id)
        )
        result = await db.execute(stmt)
        escuela_id = result.scalar_one_or_none()
        
        if escuela_id != current_user.id_escuela:
             raise HTTPException(status_code=403, detail="No tienes permiso para editar esta versión.")

    try:
        updated_version = await crud_plan_version.update(db, db_obj=version, obj_in=version_in)
        return updated_version
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar la versión.")