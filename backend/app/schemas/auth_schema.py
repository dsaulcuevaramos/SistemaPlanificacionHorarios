from pydantic import BaseModel
from typing import Optional

# Lo que envía el usuario para loguearse
class LoginRequest(BaseModel):
    username: str
    password: str

# Lo que devolvemos (Token)
class Token(BaseModel):
    access_token: str
    token_type: str

# Datos del token decodificado
class TokenData(BaseModel):
    username: Optional[str] = None

# Cómo se ve el usuario en la respuesta (sin password)
class UserDisplay(BaseModel):
    id: int
    username: str
    rol: str
    id_escuela: Optional[int] = None # clave de la lógica
    
    class Config:
        from_attributes = True


        