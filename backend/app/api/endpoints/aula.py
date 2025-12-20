from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

from app.crud.crud_aula import aula as crud_aula
from app.schemas.aula import AulaCreate, AulaResponse, AulaUpdate

router = APIRouter()

@router.get("/", response_model=List[AulaResponse])
async def read_aulas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):

    id_escuela_filter = current_user.id_escuela if current_user.id_escuela is not None else None
    
    aulas = await crud_aula.get_multi_by_escuela(
        db, id_escuela=id_escuela_filter, skip=skip, limit=limit
    )
    return aulas


@router.post("/", response_model=AulaResponse)
async def create_aula(
    aula_in: AulaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    if current_user.id_escuela is not None and aula_in.id_escuela != current_user.id_escuela:
        raise HTTPException(status_code=403, detail="No puedes crear aulas en una escuela ajena.")
        
    try:
        return await crud_aula.create(db, obj_in=aula_in)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Error de integridad (Revisar ID Escuela).")
    

@router.put("/{aula_id}", response_model=AulaResponse)
async def update_aula(
    aula_id: int,
    aula_in: AulaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
): 
    aula = await crud_aula.get(db,id=aula_id)

    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrado")
    
    if current_user.id_escuela is not None and aula.id_escuela != current_user.id_escuela:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar docentes de otra escuela."
        )

    updated_aula = await crud_aula.update(db, db_obj=aula, obj_in=aula_in)
    aula_con_relaciones = await crud_aula.get_con_relaciones(db, id=updated_aula.id)

    if not aula_con_relaciones:
        raise HTTPException(status_code=500, detail="Error al validar las relaciones del docente actualizado.")

    return aula_con_relaciones

