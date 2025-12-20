from pydantic import BaseModel
from datetime import time
from typing import Optional

class BloqueHorarioBase(BaseModel):
    dia_semana: str # Lunes, Martes, etc.
    hora_inicio: time
    hora_fin: time
    orden: int
    id_turno: int

class BloqueHorarioCreate(BloqueHorarioBase):
    pass

class BloqueHorarioResponse(BloqueHorarioBase):
    id: int
    estado: int
    class Config:
        from_attributes = True