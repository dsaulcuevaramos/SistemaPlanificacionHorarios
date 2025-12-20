from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContratoDocenteBase(BaseModel):
    id_docente: int
    fecha_inicio: date
    fecha_fin: date
    horas_tope_semanales: Optional[int] = None
    turnos_preferidos: str

class ContratoDocenteCreate(ContratoDocenteBase):
    pass

class ContratoDocenteUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    horas_tope_semanales: Optional[int] = None
    turnos_preferidos: Optional[str] = None

class ContratoDocenteResponse(ContratoDocenteBase):
    id: int
    class Config:
        from_attributes = True