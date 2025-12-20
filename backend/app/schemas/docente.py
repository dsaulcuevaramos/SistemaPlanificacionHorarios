from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import date

# Schemas de Tablas Relacionadas (Solo para anidamiento en la respuesta final)

class ContratoDocenteBase(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    horas_tope_semanales: Optional[int] = None
    turnos_preferidos: str

class DisponibilidadDocenteBase(BaseModel):
    id_periodo: int
    horas_asignadas_actuales: int

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
    
    # Opcional: Para ver los contratos y disponibilidad directamente
    contratos: List[ContratoDocenteBase] = []
    # disponibilidad: List[DisponibilidadDocenteBase] = [] # Se añade al listar el perfil

    class Config:
        from_attributes = True