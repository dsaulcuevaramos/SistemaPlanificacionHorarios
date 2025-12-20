from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

from app.crud.crud_docente import docente as crud_docente
from app.schemas.docente import DocenteCreate, DocenteResponse, DocenteUpdate

router = APIRouter()

@router.get("/", response_model=List[DocenteResponse], tags=["Docentes"])
async def read_docentes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):

    id_escuela_filter = current_user.id_escuela if current_user.id_escuela is not None else None
    
    # Aqui uso un solo método en el CRUD que maneje el filtro
    docentes = await crud_docente.get_multi_by_escuela(
        db, id_escuela=id_escuela_filter, skip=skip, limit=limit
    )
    return docentes

@router.post("/", response_model=DocenteResponse, tags=["Docentes"])
async def create_docente(
    docente_in: DocenteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    if current_user.id_escuela is not None and current_user.id_escuela != docente_in.id_escuela:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear docentes en una escuela diferente."
        )

    existing_docente = await crud_docente.get_by_dni(db, dni=docente_in.dni)
    if existing_docente:
        raise HTTPException(status_code=400, detail="El DNI ya se encuentra registrado.")

    try:
        new_docente = await crud_docente.create(db, obj_in=docente_in) # NOTA: new_docente es ahora solo el objeto base sin relaciones cargadas.     
        docente_with_relations = await crud_docente.get_with_relations(db, id=new_docente.id)

        if not docente_with_relations:      
             raise HTTPException(status_code=500, detail="Error al recuperar el docente recién creado.") # Debería ser imposible, pero por seguridad

        return docente_with_relations
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad. Asegúrate de que el 'id_escuela' exista.",
        )
    

@router.put("/{docente_id}", response_model=DocenteResponse, tags=["Docentes"])
async def update_docente(
    docente_id: int,
    docente_in: DocenteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):

    docente = await crud_docente.get(db, id=docente_id)
    
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    if current_user.id_escuela is not None and docente.id_escuela != current_user.id_escuela:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar docentes de otra escuela."
        )

    updated_docente = await crud_docente.update(db, db_obj=docente, obj_in=docente_in)
    docente_with_relations = await crud_docente.get_with_relations(db, id=updated_docente.id)

    if not docente_with_relations:
        # Si falla la recarga después del update, es un error interno del ORM
        raise HTTPException(status_code=500, detail="Error al validar las relaciones del docente actualizado.")

    return docente_with_relations


