from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud.crud_horario import horario as crud_horario
from app.schemas.horario import HorarioCreate, HorarioResponse

router = APIRouter()

@router.post("/", response_model=HorarioResponse)
async def create_horario_entry(
    obj_in: HorarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Crea una entrada en el horario. 
    Aquí irán las validaciones de cruces de aula y docente.
    """
    # TODO: Implementar lógica de validación de conflictos antes de insertar
    return await crud_horario.create(db, obj_in=obj_in)

@router.get("/periodo/{id_periodo}", response_model=list[HorarioResponse])
async def get_periodo_schedule(
    id_periodo: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await crud_horario.get_horario_periodo(db, id_periodo=id_periodo)