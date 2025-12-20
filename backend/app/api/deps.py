from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError # <-- Necesitamos JWTError para capturar fallos
from app.core.config import settings
from app.core.database import get_db
# Importamos el CRUD para buscar el usuario
from app.crud.crud_usuario import usuario as crud_usuario 
from app.models.usuario import Usuario


# ----------------------------------------------------------------------
# Esquema de Seguridad (OAuth2 / JWT)
# ----------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


# ----------------------------------------------------------------------
# Dependencia para Usuario Actual
# ----------------------------------------------------------------------

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> Usuario:
    """Decodifica el token, verifica su validez y retorna el objeto Usuario.""" 

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido, expirado o faltante",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. DECODIFICACIÓN JWT:
        # Aquí es donde fallaba antes por el auth_service. Ahora usamos python-jose
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        username: str = payload.get("sub") # Usamos 'sub' (subject) como clave principal
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        # Captura errores comunes de token: expiración, firma incorrecta, etc.
        raise credentials_exception
        
    # 2. BÚSQUEDA DEL USUARIO:
    # Usamos el CRUD que creamos (crud_usuario) para buscar el usuario
    user = await crud_usuario.get_by_username(db, username=username)
    
    if user is None:
        raise credentials_exception # El usuario existe en el token pero no en la BD
        
    return user


# ----------------------------------------------------------------------
# Dependencia para Administrador
# ----------------------------------------------------------------------

def get_current_active_admin(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Verifica que el usuario logueado tenga rol de ADMIN."""
    
    # NOTA: Usamos 'ADMIN' en mayúsculas para coincidir con la semilla de init_db.py
    if current_user.rol != 'ADMIN':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # También puedes agregar aquí la verificación de id_escuela is None si fuera SuperAdmin
    
    return current_user