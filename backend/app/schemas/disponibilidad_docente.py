from pydantic import BaseModel
from typing import Optional

class DisponibilidadDocenteBase(BaseModel):
    id_docente: int
    id_periodo: int
    horas_asignadas_actuales: int = 0

class DisponibilidadDocenteCreate(DisponibilidadDocenteBase):
    pass

class DisponibilidadDocenteUpdate(BaseModel):
    horas_asignadas_actuales: Optional[int] = None

class DisponibilidadDocenteResponse(DisponibilidadDocenteBase):
    id: int
    class Config:
        from_attributes = True