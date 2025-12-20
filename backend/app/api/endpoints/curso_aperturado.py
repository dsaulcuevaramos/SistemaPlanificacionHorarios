from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
# Importamos la instancia que creamos en el paso 2
from app.models.usuario import Usuario
from app.crud.crud_curso_aperturado import curso_aperturado as crud_apertura
from app.schemas.curso_aperturado import AperturaMasivaRequest, CursoAperturadoCreate, CursoAperturadoResponse

router = APIRouter()

# GET: Listar lo que ya existe (Para pintar los checks azules en el front)
@router.get("/{id_periodo}", response_model=List[CursoAperturadoResponse])
async def read_cursos_aperturados(
    id_periodo: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # Agrégalo para seguridad
):
    return await crud_apertura.get_by_periodo(db, id_periodo=id_periodo)

# POST: Guardar masivamente lo seleccionado
@router.post("/masiva", status_code=201)
async def apertura_masiva(
    data: AperturaMasivaRequest, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user) # Agrégalo para seguridad
):
    # 1. Obtener lo que ya existe para no duplicar
    existentes = await crud_apertura.get_by_periodo(db, id_periodo=data.id_periodo)
    ids_existentes = {c.id_curso for c in existentes}

    nuevos_registros = []
    
    # 2. Filtrar solo los nuevos
    for id_curso in data.ids_cursos:
        if id_curso not in ids_existentes:
            nuevos_registros.append(
                CursoAperturadoCreate(
                    id_curso=id_curso,
                    id_periodo=data.id_periodo,
                    cupos_proyectados=data.cupos_general
                )
            )
    
    # 3. Guardar en BD
    if nuevos_registros:
        count = await crud_apertura.create_multi(db, objs_in=nuevos_registros)
        return {"message": f"Se aperturaron {count} cursos nuevos correctamente."}
    
    return {"message": "Datos actualizados (no hubo cursos nuevos para agregar)."}