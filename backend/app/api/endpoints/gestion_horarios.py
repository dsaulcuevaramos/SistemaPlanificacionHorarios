from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.crud.crud_grupo import grupo as crud_grupo
from app.crud.crud_bloque import bloque as crud_bloque
from app.schemas.grupo import GrupoCreate, GrupoResponse
from typing import List
from app.schemas.bloque_horario import BloqueHorarioResponse, BloqueHorarioCreate

router = APIRouter()

# --- ENDPOINTS PARA BLOQUES HORARIOS ---

@router.get("/bloques/turno/{id_turno}", response_model=List[BloqueHorarioResponse])
async def read_bloques_by_turno(
    id_turno: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene los bloques configurados para un turno específico."""
    # Nota: Asegúrate que tu crud_bloque tenga el método get_by_turno
    return await crud_bloque.get_by_turno(db, id_turno=id_turno)

@router.post("/bloques/", response_model=BloqueHorarioResponse)
async def create_bloque(
    obj_in: BloqueHorarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Registra un nuevo bloque de tiempo en la rejilla."""
    return await crud_bloque.create(db, obj_in=obj_in)

@router.delete("/bloques/{id_bloque}")
async def delete_bloque(
    id_bloque: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina un bloque horario."""
    return await crud_bloque.remove(db, id=id_bloque)

# --- TUS ENDPOINTS ACTUALES (Grupos y Validar) ---
@router.get("/grupos/periodo/{id_periodo}", response_model=List[GrupoResponse])
async def read_grupos_periodo(
    id_periodo: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    return await crud_grupo.get_multi_by_periodo(db, id_periodo=id_periodo)