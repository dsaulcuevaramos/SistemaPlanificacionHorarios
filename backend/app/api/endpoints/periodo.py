from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

# Importamos la instancia 'periodo' que creamos arriba
from app.crud.crud_periodo import periodo as crud_periodo
from app.schemas.periodo import PeriodoCreate, PeriodoResponse, PeriodoUpdate
from app.services.clonacion_service import clonar_carga_academica
    
router = APIRouter()

@router.get("/", response_model=List[PeriodoResponse])
async def read_periodos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    # Usamos el método get_multi que heredas de CRUDBase
    periodos = await crud_periodo.get_multi(db, skip=skip, limit=limit)
    return periodos

@router.post("/", response_model=PeriodoResponse)
async def create_periodo(
    periodo_in: PeriodoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # 1. Usamos el método personalizado para validar duplicados
    exists = await crud_periodo.get_by_codigo(db, codigo=periodo_in.codigo)
    if exists:
        raise HTTPException(status_code=400, detail=f"El código {periodo_in.codigo} ya existe.")

    try:
        # 2. Usamos el create genérico de CRUDBase
        new_periodo = await crud_periodo.create(db, obj_in=periodo_in)
        return new_periodo
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al crear periodo.")

@router.put("/{periodo_id}", response_model=PeriodoResponse)
async def update_periodo(
    periodo_id: int,
    periodo_in: PeriodoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # 1. Buscamos con el get genérico
    periodo_obj = await crud_periodo.get(db, id=periodo_id)
    if not periodo_obj:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    
    # 2. Actualizamos con el update genérico
    updated = await crud_periodo.update(db, db_obj=periodo_obj, obj_in=periodo_in)
    return updated


@router.get("/{periodo_id}", response_model=PeriodoResponse)
async def read_periodo(
    periodo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    # Usamos el crud base .get que ya tienes
    periodo = await crud_periodo.get(db, id=periodo_id)
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")
    return periodo
    

@router.post("/clonar/{id_origen}/{id_destino}")
async def endpoint_clonar_periodo(
    id_origen: int, 
    id_destino: int, 
    db: AsyncSession = Depends(get_db)
):
    resultado = await clonar_carga_academica(db, id_origen, id_destino)
    
    if resultado["status"] == "error":
        raise HTTPException(status_code=400, detail=resultado["message"])
        
    return resultado