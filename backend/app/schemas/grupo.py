from pydantic import BaseModel
from typing import Optional

class GrupoBase(BaseModel):
    nombre: str
    vacantes: int
    id_curso_aperturado: int
    id_docente: Optional[int] = None # Puede ser nulo inicialmente 
    id_turno: int

class GrupoCreate(GrupoBase):
    pass

class GrupoUpdate(BaseModel):
    nombre: Optional[str] = None
    vacantes: Optional[int] = None
    id_docente: Optional[int] = None
    id_turno: Optional[int] = None
    estado: Optional[int] = None

class GrupoResponse(GrupoBase):
    id: int
    estado: int
    class Config:
        from_attributes = True