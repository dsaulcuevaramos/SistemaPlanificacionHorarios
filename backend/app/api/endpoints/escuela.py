from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

# Imports de base de datos y seguridad
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

# Imports de CRUD y Schemas de Escuela
from app.crud.crud_escuela import escuela as crud_escuela
from app.schemas.escuela import EscuelaCreate, EscuelaUpdate, EscuelaResponse

router = APIRouter()

@router.get("/", response_model=List[EscuelaResponse], tags=["Escuelas"])
async def read_escuelas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Obtener lista de escuelas.
    - Si es SuperAdmin: Devuelve todas.
    - Si es Usuario de Escuela: Devuelve solo su escuela asignada.
    """
    
    # Si el usuario pertenece a una escuela, solo devolvemos esa (como lista de 1 elemento)
    if current_user.id_escuela is not None:
        escuela = await crud_escuela.get(db, id=current_user.id_escuela)
        return [escuela] if escuela else []
    
    # Si es admin (id_escuela is None), devuelve todas paginadas
    escuelas = await crud_escuela.get_multi(db, skip=skip, limit=limit)
    return escuelas


@router.post("/", response_model=EscuelaResponse, tags=["Escuelas"])
async def create_escuela(
    escuela_in: EscuelaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Crear nueva escuela.
    - Restricción: Solo usuarios sin escuela asignada (Admins) deberían crear escuelas nuevas.
    """
    
    if current_user.id_escuela is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador global para crear nuevas escuelas."
        )

    try:
        # Creamos la escuela usando el CRUD base heredado
        new_escuela = await crud_escuela.create(db, obj_in=escuela_in)
        return new_escuela
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la escuela. Es posible que el nombre ya exista.",
        )


@router.put("/{escuela_id}", response_model=EscuelaResponse, tags=["Escuelas"])
async def update_escuela(
    escuela_id: int,
    escuela_in: EscuelaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Actualizar una escuela existente.
    """
    escuela = await crud_escuela.get(db, id=escuela_id)
    
    if not escuela:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")

    # Verificar permisos:
    # Si el usuario tiene escuela asignada Y esa escuela no es la que intenta editar -> Error
    if current_user.id_escuela is not None and current_user.id_escuela != escuela_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar los datos de otra escuela."
        )

    try:
        updated_escuela = await crud_escuela.update(db, db_obj=escuela, obj_in=escuela_in)
        return updated_escuela
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar. Verifica que los datos sean válidos.",
        )