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

class GrupoResponse(BaseModel):
    id: int
    nombre: str
    vacantes: int
    docente_nombre: Optional[str] = "Sin Asignar"
    turno_nombre: str

    id_curso_aperturado: int
    ciclo: Optional[int] = None 
    curso_nombre: Optional[str] = None
    class Config:
        from_attributes = True

# Esquema para la CREACIÓN MASIVA (La magia)
class GrupoCreateMasivo(BaseModel):
    id_curso_aperturado: int
    id_docente: Optional[int] = None # Puede ser null si aún no defines al profe
    id_turno: int
    cantidad_grupos: int = 1         # Por defecto crea 1 (Grupo A)
    vacantes_por_grupo: int = 40