from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
# Nota: YA NO IMPORTAMOS get_current_user porque es público
from app.crud.crud_escuela import escuela as crud_escuela
from app.schemas.escuela import EscuelaCreate, EscuelaUpdate, EscuelaResponse

router = APIRouter()

# 1. LISTAR ESCUELAS (GET) - PÚBLICO
@router.get("/", response_model=List[EscuelaResponse])
async def read_escuelas(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtener lista de todas las escuelas.
    No requiere autenticación.
    """
    escuelas = await crud_escuela.get_multi(db, skip=skip, limit=limit)
    return escuelas


# 2. CREAR ESCUELA (POST) - PÚBLICO
@router.post("/", response_model=EscuelaResponse)
async def create_escuela(
    escuela_in: EscuelaCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Crear una nueva escuela.
    No requiere autenticación.
    """
    try:
        # Intentamos crear la escuela directamente
        new_escuela = await crud_escuela.create(db, obj_in=escuela_in)
        return new_escuela
        
    except IntegrityError as e:
        await db.rollback()
        # Manejo básico de errores de duplicidad
        # (Si el nombre de la escuela es unique en la BD)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al crear la escuela. Es posible que el nombre ya exista."
        )
    except Exception as e:
        await db.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error interno al crear la escuela."
        )


# 3. ACTUALIZAR ESCUELA (PUT) - PÚBLICO
@router.put("/{escuela_id}", response_model=EscuelaResponse)
async def update_escuela(
    escuela_id: int,
    escuela_in: EscuelaUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Actualizar datos de una escuela por ID.
    No requiere autenticación.
    """
    escuela = await crud_escuela.get(db, id=escuela_id)
    
    if not escuela:
        raise HTTPException(status_code=404, detail="Escuela no encontrada")

    try:
        updated_escuela = await crud_escuela.update(db, db_obj=escuela, obj_in=escuela_in)
        return updated_escuela
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error al actualizar. Verifica que los datos sean válidos.",
        )