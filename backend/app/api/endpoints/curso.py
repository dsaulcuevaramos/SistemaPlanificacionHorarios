from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from app.core.database import get_db
from app.crud.crud_curso import curso as crud_curso
from app.schemas.curso import CursoCreate, CursoResponse, CursoUpdate

from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.models.curso import Curso
from app.models.plan_version import PlanVersion
from app.models.plan_estudio import PlanEstudio

from sqlalchemy import insert, delete, and_
from app.models.curso import curso_requisito_assoc

router = APIRouter()

# Función auxiliar local para cargar relaciones y evitar duplicar código
async def get_curso_with_relations_helper(db: AsyncSession, id: int) -> Optional[Curso]:
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Curso)
        .options(
            selectinload(Curso.plan_version).selectinload(PlanVersion.plan_estudio)
        )
        .where(Curso.id == id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


@router.get("/", response_model=List[CursoResponse], tags=["Cursos"])
async def read_cursos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    id_escuela_filter = current_user.id_escuela

    cursos = await crud_curso.get_multi_by_escuela(
        db, id_escuela=id_escuela_filter, skip=skip, limit=limit
    )
    return cursos


@router.post("/", response_model=CursoResponse, tags=["Cursos"])
async def create_curso(
    curso_in: CursoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    if curso_in.paridad not in ["PAR", "IMPAR", "AMBOS"]: # Validación de Paridad
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'paridad' debe ser 'PAR', 'IMPAR' o 'AMBOS'."
        )
    if current_user.id_escuela is not None:
        stmt = (
            select(PlanEstudio.id_escuela)
            .join(PlanVersion, PlanVersion.id_plan_estudio == PlanEstudio.id)
            .where(PlanVersion.id == curso_in.id_plan_version)
        )
        result = await db.execute(stmt)
        escuela_id_del_plan = result.scalar_one_or_none()

        if not escuela_id_del_plan:
             raise HTTPException(status_code=404, detail="La versión del plan especificada no existe.")
             
        if escuela_id_del_plan != current_user.id_escuela:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No puedes crear un curso en un Plan de Estudio de otra escuela."
            )
    try:    
        new_curso = await crud_curso.create(db, obj_in=curso_in)#Crear el curso
        curso_with_relations = await get_curso_with_relations_helper(db, id=new_curso.id) #Recargar relaciones para el Response Model
        return curso_with_relations

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error de integridad. Verifica los datos enviados.",)


@router.put("/{curso_id}", response_model=CursoResponse, tags=["Cursos"])
async def update_curso(
    curso_id: int,
    curso_in: CursoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    curso = await crud_curso.get(db, id=curso_id) # Verificar si el curso existe
    if not curso:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")
    
    stmt = ( # Esta consulta navega Curso -> PlanVersion -> PlanEstudio
        select(PlanEstudio.id_escuela)
        .select_from(Curso)  # <--- CRÍTICO!!!!!!!!!!!!!!!!!! Define el punto de partida explícito xd
        .join(PlanVersion, Curso.id_plan_version == PlanVersion.id)
        .join(PlanEstudio, PlanVersion.id_plan_estudio == PlanEstudio.id)
        .where(Curso.id == curso_id))
    
    result = await db.execute(stmt)
    id_escuela_del_curso = result.scalar_one_or_none()

    # Si el usuario tiene escuela asignada, verificamos que coincida
    if current_user.id_escuela and id_escuela_del_curso != current_user.id_escuela:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permiso para editar este curso (pertenece a otra escuela).")
    if curso_in.paridad and curso_in.paridad not in ["PAR", "IMPAR", "AMBOS"]: # Validaciones adicionales de lógica de negocio (Paridad)
         raise HTTPException(status_code=400, detail="El campo 'paridad' debe ser 'PAR', 'IMPAR' o 'AMBOS'.")

    try: # Actualizar el curso
        updated_curso = await crud_curso.update(db, db_obj=curso, obj_in=curso_in)
        curso_final = await get_curso_with_relations_helper(db, id=updated_curso.id)
        return curso_final
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Error de integridad al actualizar.")
    
#para la relación
@router.post("/{curso_id}/requisitos/{requisito_id}", status_code=201)
async def add_requisito(
    curso_id: int,
    requisito_id: int,
    id_plan_version: int, # Necesitamos saber en qué versión ocurre esto para que carge de cada uno ps
    db: AsyncSession = Depends(get_db)
):
    if curso_id == requisito_id: #Evitar ciclos simples (A->A)
        raise HTTPException(status_code=400, detail="Un curso no puede ser requisito de sí mismo.")

    try:    # Inserto en la tabla intermedia bien insertao
        stmt = insert(curso_requisito_assoc).values(
            id_curso=curso_id,              # El curso "Hijo" 
            id_curso_requisito=requisito_id, # El curso "Padre" 
            id_plan_version=id_plan_version)
        await db.execute(stmt)
        await db.commit()
        return {"msg": "Requisito agregado"}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="El requisito ya existe o hay un error de datos.")
    
    
@router.delete("/{curso_id}/requisitos/{requisito_id}")
async def remove_requisito(
    curso_id: int,
    requisito_id: int,
    db: AsyncSession = Depends(get_db)
):

    stmt = delete(curso_requisito_assoc).where(  #rpara romperle la relación pero fisicamente para que no exite nuevamente
        and_(
            curso_requisito_assoc.c.id_curso == curso_id,
            curso_requisito_assoc.c.id_curso_requisito == requisito_id
        ))
    await db.execute(stmt)
    await db.commit()
    return {"msg": "Requisito eliminado"}