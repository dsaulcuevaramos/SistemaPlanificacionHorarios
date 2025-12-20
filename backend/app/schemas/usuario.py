from typing import Optional
from pydantic import BaseModel, EmailStr

# Base común
class UsuarioBase(BaseModel):
    username: str
    rol: str # ADMIN, DIRECTOR, SECRETARIA
    email: Optional[EmailStr] = None # EmailStr valida formato correo automáticamente
    dni: Optional[str] = None
    id_escuela: Optional[int] = None # Puede ser null si es SuperAdmin
    estado: int = 1

# Para Crear (Password obligatorio)
class UsuarioCreate(UsuarioBase):
    password: str
    email: EmailStr 
    dni: str

# Para Actualizar (Todo opcional, incluido password)
class UsuarioUpdate(UsuarioBase):
    username: Optional[str] = None
    password: Optional[str] = None
    rol: Optional[str] = None
    email: Optional[EmailStr] = None
    dni: Optional[str] = None
    id_escuela: Optional[int] = None
    estado: int = 1

# Para Respuesta (SIN PASSWORD)
class UsuarioResponse(UsuarioBase):
    id: int
    id_escuela: Optional[int]
    estado: int
    # Podrías anidar la escuela aquí si quisieras ver el nombre, 
    # pero requiere configurar la relación en Pydantic.
    class Config:
        from_attributes = True

class PasswordRecovery(BaseModel):
    username_or_email: str
    dni: str

class PasswordReset(BaseModel):
    username_or_email: str
    dni: str
    new_password: str