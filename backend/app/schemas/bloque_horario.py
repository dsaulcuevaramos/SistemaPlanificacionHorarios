from pydantic import BaseModel
from datetime import time
from typing import List, Optional

# Esquema base siguiendo tu DB 
class BloqueHorarioBase(BaseModel):
    dia_semana: str  # Lunes, Martes, etc.
    hora_inicio: time
    hora_fin: time
    orden: int
    id_turno: int

class BloqueHorarioCreate(BloqueHorarioBase):
    pass


class IntervaloSchema(BaseModel):
    inicio: time
    fin: time
    orden: int

# Esquema para generación masiva
class BloqueMasivoCreate(BaseModel):
    id_turno: int
    dias: List[str]  # ["Lunes", "Martes", "Miércoles"...]
    intervalos: List[IntervaloSchema] # [{"inicio": "07:00", "fin": "07:45", "orden": 1}, ...]

class BloqueHorarioResponse(BloqueHorarioBase):
    id: int
    estado: int
    class Config:
        from_attributes = True