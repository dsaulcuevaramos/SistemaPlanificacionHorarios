from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import date


# Schema principal: Docente
class DocenteBase(BaseModel):
    dni: str
    nombre: str
    apellido: str
    email: EmailStr
    telefono: Optional[str] = None
    tipo_docente: str
    horas_maximas_semanales: int
    id_escuela: int

class DocenteCreate(DocenteBase):
    pass

class DocenteUpdate(DocenteBase):
    dni: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    tipo_docente: Optional[str] = None
    horas_maximas_semanales: Optional[int] = None
    id_escuela: Optional[int] = None
    estado: Optional[int] = None

class DocenteResponse(DocenteBase):
    id: int
    estado: int

    class Config:
        from_attributes = True