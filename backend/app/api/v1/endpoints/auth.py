"""
# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db # Importa la función get_db
from app.crud import crud_usuario as crud
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Autenticación"])

# 1. Endpoint para REGISTRO de un nuevo usuario
@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    usuario_in: UsuarioCreate,
    db: AsyncSession = Depends(get_db)
):
    # 1. Verificar si el usuario ya existe
    existing_user = await crud.usuario.get_by_username(db, username=usuario_in.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
        
    # 2. Hashear la contraseña
    hashed_password = auth_service.get_password_hash(usuario_in.password)
    
    # 3. Crear el objeto a insertar
    usuario_data = usuario_in.model_dump(exclude={'password'})
    usuario_data['password'] = hashed_password
    
    new_user = await crud.usuario.create(db, obj_in=usuario_data)
    
    return new_user

# 2. Endpoint para LOGIN y generación de Token
@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: UsuarioLogin,
    db: AsyncSession = Depends(get_db)
):
    user = await crud.usuario.get_by_username(db, username=form_data.username)
    
    if not user or not auth_service.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Crear el token con datos de multi-tenancy
    access_token_data = {
        "username": user.username,
        "id": user.id,
        "id_escuela": user.id_escuela, # <-- DATO CLAVE PARA EL FILTRADO
        "rol": user.rol
    }
    
    access_token = auth_service.create_access_token(data=access_token_data)
    
    return {"access_token": access_token, "token_type": "bearer"}"""