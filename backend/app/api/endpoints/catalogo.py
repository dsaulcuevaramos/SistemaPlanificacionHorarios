from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.catalogo import CatalogoCreate, CatalogoUpdate, CatalogoResponse
from app.crud.crud_catalogo import catalogo as crud_catalogo # Instancia

router = APIRouter()

@router.get("/", response_model=List[CatalogoResponse])
async def read_catalogos(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    # ¡Mira qué limpio! Una sola línea llama a la lógica de base de datos
    return await crud_catalogo.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=CatalogoResponse)
async def create_catalogo(
    item_in: CatalogoCreate, 
    db: AsyncSession = Depends(get_db)
):
    return await crud_catalogo.create(db, obj_in=item_in)