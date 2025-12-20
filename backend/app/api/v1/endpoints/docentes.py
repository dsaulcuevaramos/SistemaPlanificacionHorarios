"""

# app/api/v1/endpoints/docentes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps # get_db, get_current_user, get_current_active_admin
from app.crud import crud_docente as crud
from app.schemas.docente import DocenteCreate, DocenteUpdate, DocenteResponse 
from app.models.usuario import Usuario 

router = APIRouter(prefix="/docentes", tags=["Docentes"])

# --- ENDPOINT 1: CREAR DOCENTE ---
@router.post("/", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
async def create_docente(
    docente_in: DocenteCreate,
    db: AsyncSession = Depends(deps.get_db),
    # Solo permite la creación a usuarios logueados con rol ADMIN
    current_admin: Usuario = Depends(deps.get_current_active_admin) 
):
    # 1. Validación de DNI (Regla de negocio)
    existing_docente = await crud.docente.get_by_dni(db, dni=docente_in.dni)
    if existing_docente:
        raise HTTPException(status_code=400, detail="Ya existe un docente registrado con este DNI.")

    # 2. Inyección de la Seguridad (Multi-tenancy)
    docente_data = docente_in.model_dump()
    # El id_escuela se toma del JWT del usuario logueado, no del cuerpo de la petición
    docente_data['id_escuela'] = current_admin.id_escuela
    
    return await crud.docente.create(db, obj_in=docente_data)


# --- ENDPOINT 2: LISTAR DOCENTES ---
@router.get("/", response_model=list[DocenteResponse])
async def read_docentes(
    db: AsyncSession = Depends(deps.get_db),
    # Protegido, pero disponible para cualquier usuario logueado de la misma escuela
    current_user: Usuario = Depends(deps.get_current_user) 
):
    # FILTRADO DE SEGURIDAD: Solo lista docentes de la escuela del usuario
    docentes = await crud.docente.get_multi_by_escuela(db, id_escuela=current_user.id_escuela)
    return docentes


# --- ENDPOINT 3: LEER DOCENTE POR ID (Detalle) ---
@router.get("/{docente_id}", response_model=DocenteResponse)
async def read_docente(
    docente_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user)
):
    docente_obj = await crud.docente.get(db, id=docente_id)
    
    if not docente_obj:
        raise HTTPException(status_code=404, detail="Docente no encontrado.")
        
    # VALIDACIÓN DE SEGURIDAD: Asegura que el docente pertenezca a la misma escuela que el usuario
    if docente_obj.id_escuela != current_user.id_escuela:
        raise HTTPException(status_code=403, detail="Acceso denegado a este recurso.")
        
    return docente_obj


# --- ENDPOINT 4: ACTUALIZAR DOCENTE ---
@router.put("/{docente_id}", response_model=DocenteResponse)
async def update_docente(
    docente_id: int,
    docente_in: DocenteUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_admin: Usuario = Depends(deps.get_current_active_admin) # Requiere Admin
):
    docente_obj = await crud.docente.get(db, id=docente_id)
    
    if not docente_obj or docente_obj.id_escuela != current_admin.id_escuela:
        raise HTTPException(status_code=404, detail="Docente no encontrado o acceso denegado.")

    return await crud.docente.update(db, db_obj=docente_obj, obj_in=docente_in)"""