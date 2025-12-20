"""
# backend/app/services/validador.py
from app.core.handler.exeptions import CruceHorarioError, DocenteNoDisponibleError

async def validar_disponibilidad_docente(db, docente_id: int, hora_inicio: str, dia: str):
    # Imaginemos que consultas la BD y encuentras que ya tiene clase
    tiene_clase = await db.check_clase_existente(docente_id, hora_inicio, dia)
    
    if tiene_clase:
        # ¡AQUÍ ES EL "THROW"!
        # Esto detiene todo y manda la señal de error hacia arriba
        raise DocenteNoDisponibleError(docente_nombre="Diego Cueva")
    
    return True

"""
# app/services/auth_service.py

"""
from datetime import datetime, timedelta
from typing import Optional, Final
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

# Contexto de hash para contraseñas (bcrypt es el estándar por seguridad)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    #Verifica si la contraseña plana coincide con el hash almacenado.
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    #Genera el hash de una contraseña para almacenar en BD.
    return pwd_context.hash(password)

def create_access_token(*, data: dict, expires_delta: Optional[timedelta] = None) -> str:
    #Crea un token de acceso JWT con datos como id_escuela.
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    #Decodifica el token de acceso JWT.
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None
    
    """