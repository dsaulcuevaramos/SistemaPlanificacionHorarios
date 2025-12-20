"""# app/api/v1/endpoints/requisitos.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps # get_db, get_current_user, get_current_active_admin
from app.crud.requisito_curso import requisito_curso as crud_req
from app.schemas.curso import (
    RequisitoCursoCreate, 
    RequisitoCursoRead, 
    CursoReadSimple # Para validación de existencia
)
from app.crud.curso import curso as crud_curso # Para validar que los IDs existan
from app.models.usuario import Usuario 

# NOTA: Usamos rutas anidadas para operar sobre un curso específico
router = APIRouter(prefix="/cursos", tags=["Prerrequisitos / Malla"])

# --- DEPENDENCIAS DE VALIDACIÓN Y SEGURIDAD ---

async def get_valid_course(db: AsyncSession, id: int, current_user: Usuario):
    """"""Obtiene y valida que un curso pertenezca a la escuela del usuario logueado.""""""
    curso_obj = await crud_curso.get(db, id=id)
    if not curso_obj:
        raise HTTPException(status_code=404, detail=f"Curso con ID {id} no encontrado.")

    # Asumiendo que Curso tiene id_plan_version, y PlanVersion tiene id_plan, 
    # y PlanEstudio tiene id_escuela. Se requiere un join o lógica en CRUD/Service 
    # para obtener el id_escuela del curso. Por ahora, validamos a nivel de servicio.
    # *** REGLA DE NEGOCIO PENDIENTE: Validar que el curso pertenezca a la escuela del usuario ***
    
    # if curso_obj.id_escuela != current_user.id_escuela: # << Esta propiedad no existe en Curso
    #     raise HTTPException(status_code=403, detail="Acceso denegado a este curso.")
    
    return curso_obj

# --- ENDPOINT 1: AÑADIR PRERREQUISITO ---
@router.post(
    "/{id_curso_dependiente}/requisitos", 
    response_model=RequisitoCursoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir un prerrequisito a un curso"
)
async def add_prerequisite(
    id_curso_dependiente: int,
    req_in: RequisitoCursoCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: Usuario = Depends(deps.get_current_active_admin)
):
    # 1. Validación: Que el curso dependiente exista y pertenezca a la escuela (implícito si el admin lo ve)
    await get_valid_course(db, id=id_curso_dependiente, current_user=current_admin)
    
    # 2. Validación: Que el curso requisito exista
    await get_valid_course(db, id=req_in.id_curso_requisito, current_user=current_admin)
    
    # 3. Validación: Un curso no puede ser requisito de sí mismo
    if id_curso_dependiente == req_in.id_curso_requisito:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Un curso no puede ser requisito de sí mismo."
         )
         
    try:
        new_req = await crud_req.create(
            db=db, 
            id_curso_dependiente=id_curso_dependiente, 
            obj_in=req_in
        )
        return new_req
    except Exception as e:
        # Manejo de la violación de restricción única (ya existe la relación)
        if "duplicate key value" in str(e): # Mensaje común de PostgreSQL/SQLAlchemy
             raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esta relación de prerrequisito ya existe."
            )
        raise e

# --- ENDPOINT 2: ELIMINAR PRERREQUISITO ---
@router.delete(
    "/{id_curso_dependiente}/requisitos/{id_curso_requisito}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un prerrequisito de un curso"
)
async def remove_prerequisite(
    id_curso_dependiente: int,
    id_curso_requisito: int,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: Usuario = Depends(deps.get_current_active_admin)
):
    """"""
    Elimina la dependencia del curso_requisito sobre el curso_dependiente.
    """"""S
    # 1. Validación de existencia (implícito en la eliminación, pero buena práctica)
    await get_valid_course(db, id=id_curso_dependiente, current_user=current_admin)
    
    success = await crud_req.remove(
        db=db, 
        id_curso_dependiente=id_curso_dependiente, 
        id_curso_requisito=id_curso_requisito
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La relación de prerrequisito no fue encontrada."
        )
    # 204 No Content es la respuesta estándar para eliminaciones exitosas.
    return"""