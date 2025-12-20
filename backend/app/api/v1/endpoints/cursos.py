"""

# app/api/v1/endpoints/cursos.py (ACTUALIZADO)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps # get_db, get_current_user, get_current_active_admin
from app.crud.curso import curso as crud # Importamos el CRUD que acabamos de crear
from app.schemas.curso import CursoCreate, CursoUpdate, CursoResponse 
from app.models.usuario import Usuario 
# Importamos PlanVersion para validar que el curso se cree en un plan válido
from app.crud.plan_version import plan_version as crud_plan # Asume que tienes este CRUD

router = APIRouter(prefix="/cursos", tags=["Cursos"])

# --- ENDPOINT 1: CREAR CURSO ---
@router.post("/", response_model=CursoResponse, status_code=status.HTTP_201_CREATED)
async def create_curso(
    curso_in: CursoCreate,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: Usuario = Depends(deps.get_current_active_admin) 
):
    # 1. Validación de Plan de Estudios (Regla de negocio y Multi-tenancy)
    plan_version = await crud_plan.get(db, id=curso_in.id_plan_version)
    if not plan_version:
        raise HTTPException(status_code=404, detail="Versión de Plan de Estudios no encontrada.")
        
    # Validar que el Plan de Estudios pertenezca a la escuela del usuario (asumiendo lógica en PlanVersion/PlanEstudio)
    if plan_version.plan_estudio.id_escuela != current_admin.id_escuela:
        raise HTTPException(status_code=403, detail="El plan de estudios no pertenece a su escuela.")

    # 2. Validación de unicidad de Código dentro del Plan
    existing_curso = await crud.get_by_codigo(
        db, codigo=curso_in.codigo, id_plan_version=curso_in.id_plan_version
    )
    if existing_curso:
        raise HTTPException(status_code=400, detail=f"Ya existe el curso con código {curso_in.codigo} en esta versión del plan.")
    
    # 3. Creación
    return await crud.create(db, obj_in=curso_in)


# --- ENDPOINT 2: LISTAR CURSOS ---
@router.get("/", response_model=list[CursoResponse])
async def read_cursos(
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user), 
    id_plan_version: int | None = None # Filtro opcional
):
    """"""
    Lista todos los cursos de la escuela del usuario logueado, con filtro opcional por 
    versión de Plan de Estudios.
    """"""
    # FILTRADO DE SEGURIDAD: Solo lista cursos cuyo plan pertenezca a la escuela del usuario
    cursos = await crud.get_multi_by_escuela_and_plan(
        db, 
        id_escuela=current_user.id_escuela, 
        id_plan_version=id_plan_version
    )
    return cursos


# --- ENDPOINT 3: LEER CURSO POR ID (Detalle) ---
@router.get("/{curso_id}", response_model=CursoResponse)
async def read_curso(
    curso_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    curso_obj = await crud.get(db, id=curso_id)
    
    if not curso_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")
        
    # VALIDACIÓN DE SEGURIDAD: Asegura que el curso pertenezca a la misma escuela que el usuario
    # Requiere cargar la relación PlanVersion -> PlanEstudio -> id_escuela
    if curso_obj.plan_version.plan_estudio.id_escuela != current_user.id_escuela:
        raise HTTPException(status_code=403, detail="Acceso denegado a este recurso.")
        
    return curso_obj


# --- ENDPOINT 4: ACTUALIZAR CURSO ---
@router.put("/{curso_id}", response_model=CursoResponse)
async def update_curso(
    curso_id: int,
    curso_in: CursoUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: Usuario = Depends(deps.get_current_active_admin) # Requiere Admin
):
    curso_obj = await crud.get(db, id=curso_id)
    
    if not curso_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")

    # VALIDACIÓN DE SEGURIDAD: 
    if curso_obj.plan_version.plan_estudio.id_escuela != current_admin.id_escuela:
        raise HTTPException(status_code=403, detail="Acceso denegado a este curso.")
        
    # 1. Validación de unicidad de Código (si se intenta cambiar el código)
    if curso_in.codigo and curso_in.codigo != curso_obj.codigo:
        existing_curso = await crud.get_by_codigo(
            db, codigo=curso_in.codigo, id_plan_version=curso_obj.id_plan_version
        )
        if existing_curso:
            raise HTTPException(status_code=400, detail=f"Ya existe el curso con código {curso_in.codigo} en este plan.")

    return await crud.update(db, db_obj=curso_obj, obj_in=curso_in)
    
# --- ENDPOINT 5: ELIMINAR CURSO (Lógico) ---
@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_curso(
    curso_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: Usuario = Depends(deps.get_current_active_admin)
):
    curso_obj = await crud.get(db, id=curso_id)
    
    if not curso_obj:
        raise HTTPException(status_code=404, detail="Curso no encontrado.")

    # VALIDACIÓN DE SEGURIDAD:
    if curso_obj.plan_version.plan_estudio.id_escuela != current_admin.id_escuela:
        raise HTTPException(status_code=403, detail="Acceso denegado a este curso.")

    # Eliminación lógica (cambio de estado)
    await crud.update(db, db_obj=curso_obj, obj_in={"estado": 0})
    return"""