from typing import Optional
from pydantic import BaseModel

class EscuelaBase(BaseModel):
    nombre: str
    facultad: Optional[str] = None

class EscuelaCreate(EscuelaBase):
    pass

class EscuelaUpdate(EscuelaBase):
    nombre: Optional[str] = None
    facultad: Optional[str] = None

class EscuelaResponse(EscuelaBase):
    id: int
    estado: int

    class Config:
        from_attributes = True