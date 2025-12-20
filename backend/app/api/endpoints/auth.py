from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.crud.crud_usuario import usuario as crud_usuario
from app.schemas.auth_schema import Token

from app.schemas.usuario import PasswordRecovery, PasswordReset
from app.core.security import get_password_hash, verify_password

from app.schemas.usuario import UsuarioResponse
from app.models.usuario import Usuario

router = APIRouter()

@router.post("/login")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Any:
 
    user = await crud_usuario.authenticate(
        db, username_or_email=form_data.username, password=form_data.password)# Autenticación 
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.estado == 0:
        raise HTTPException(status_code=400, detail="Usuario inactivo.")
    
    access_token = create_access_token(  # Crear Token
        data={"sub": user.username, "id_escuela": user.id_escuela})
    user_response = UsuarioResponse.model_validate(user)# Convierto el objeto complejo de BD a un JSON limpio

    return {"access_token": access_token, "token_type": "bearer","user": user_response      # Aquí enviamos el dato limpio
    }

@router.post("/recover-password", response_model=dict)
async def recover_password(
    recovery_in: PasswordRecovery,
    db: AsyncSession = Depends(get_db)
):
    user: Usuario | None = await crud_usuario.get_by_username_or_email( # Buscar usuario por username o email
        db, username_or_email=recovery_in.username_or_email)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario o email no encontrado.")

    if user.dni != recovery_in.dni:  # Validar DNI
        raise HTTPException(status_code=403, detail="DNI incorrecto para este usuario.")

    return {
        "message": "Validación exitosa",
        "current_password_hash": user.password,
        "username": user.username
    }


@router.post("/reset-password", response_model=dict)
async def reset_password(
    reset_in: PasswordReset,
    db: AsyncSession = Depends(get_db)
):
    user: Usuario | None = await crud_usuario.get_by_username_or_email( # Buscar usuario por username o email
        db, username_or_email=reset_in.username_or_email)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario o email no encontrado.")


    if user.dni != reset_in.dni:        # Validar DNI
        raise HTTPException(status_code=403, detail="DNI incorrecto.")
        
    
    hashed_password = get_password_hash(reset_in.new_password)  #Genera el hash de la nueva contraseña
    
    user.password = hashed_password
    db.add(user)
    await db.commit()
    
    return {"message": "Contraseña actualizada correctamente"}
