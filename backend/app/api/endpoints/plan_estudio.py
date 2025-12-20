from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

from app.crud.crud_plan_estudio import plan_estudio as crud_plan_estudio
from app.schemas.plan_estudio import PlanEstudioCreate, PlanEstudioResponse, PlanEstudioUpdate

router = APIRouter()

@router.get("/", response_model=List[PlanEstudioResponse])
async def read_planes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):

    if current_user.id_escuela is None:
        # SuperAdmin: verá todos
        planes = await crud_plan_estudio.get_multi(db, skip=skip, limit=limit)
    else:
        planes = await crud_plan_estudio.get_multi_by_escuela(
            db, id_escuela=current_user.id_escuela, skip=skip, limit=limit
        )
    return planes

@router.post("/", response_model=PlanEstudioResponse)
async def create_plan(
    plan_in: PlanEstudioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    if current_user.id_escuela is not None:
        if plan_in.id_escuela != current_user.id_escuela:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear un plan para una escuela diferente a la tuya.")
    try:
        new_plan = await crud_plan_estudio.create(db, obj_in=plan_in)
        return new_plan
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear el plan. Verifica que no exista un plan con el mismo nombre."
        )

@router.put("/{plan_id}", response_model=PlanEstudioResponse)
async def update_plan(
    plan_id: int,
    plan_in: PlanEstudioUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    plan = await crud_plan_estudio.get(db, id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de estudio no encontrado.")

    if current_user.id_escuela is not None and plan.id_escuela != current_user.id_escuela:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar este plan.")

    try:
        updated_plan = await crud_plan_estudio.update(db, db_obj=plan, obj_in=plan_in)
        return updated_plan
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error al actualizar el plan.")