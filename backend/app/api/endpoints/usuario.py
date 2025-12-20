from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.crud.crud_usuario import usuario as crud_usuario
from app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

from app.api.deps import get_current_user # <--- IMPORTANTE: Importar la dependencia de seguridad
from app.models.usuario import Usuario # Importar el modelo

router = APIRouter()

# --- NUEVA RUTA MOVIDA AQUÍ ---
@router.get("/me", response_model=UsuarioResponse)
async def read_users_me(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene el usuario actual basado en el token.
    Ruta final esperada: /api/v1/usuarios/me
    """
    return current_user
# ------------------------------

# 1. LISTAR USUARIOS (GET)
@router.get("/", response_model=List[UsuarioResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    users = await crud_usuario.get_multi(db, skip=skip, limit=limit)
    return users


# 2. CREAR USUARIO (POST)
@router.post("/", response_model=UsuarioResponse)
async def create_user(
    usuario_in: UsuarioCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Verificamos si ya existe el username
    user = await crud_usuario.get_by_username(db, username=usuario_in.username)
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe.")
    
    # Verificamos si ya existe el DNI (si se envía)
    if usuario_in.dni:
        user_dni = await crud_usuario.get_by_dni(db, dni=usuario_in.dni)
        if user_dni:
            raise HTTPException(status_code=400, detail="El DNI ya está registrado.")

    new_user = await crud_usuario.create(db, obj_in=usuario_in)
    return new_user


# 3. ACTUALIZAR (CAMBIAR PASSWORD O DATOS) (PUT)
@router.put("/{user_id}", response_model=UsuarioResponse)
async def update_user(
    user_id: int, 
    usuario_in: UsuarioUpdate, 
    db: AsyncSession = Depends(get_db)
):
    user = await crud_usuario.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    try:
        # Aquí es donde ocurre la magia (y los errores)
        user = await crud_usuario.update(db, db_obj=user, obj_in=usuario_in)
        
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig)
        if "unique constraint" in error_msg:
            raise HTTPException(status_code=400, detail="El email, usuario o DNI ya existen.")
        elif "foreign key constraint" in error_msg:
            raise HTTPException(status_code=400, detail="La escuela no existe.")
        else:
            raise HTTPException(status_code=400, detail=f"Error DB: {error_msg}")

    except Exception as e:
        # ESTO CAPTURARÁ EL ERROR DE BCRYPT O CUALQUIER OTRO BUG DE CÓDIGO
        print(f"ERROR CRÍTICO: {str(e)}") # Míralo en la terminal
        raise HTTPException(
            status_code=500, 
            detail=f"Error del Servidor (Probablemente Hashing): {str(e)}"
        )
    return user

    # El CRUD ya se encarga de hashear el password si viene en usuario_in
    #user = await crud_usuario.update(db, db_obj=user, obj_in=usuario_in)
    #return user