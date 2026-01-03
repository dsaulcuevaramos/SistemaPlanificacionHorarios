from typing import Optional, List
from pydantic import BaseModel
from datetime import time

class TurnoBase(BaseModel):
    nombre: str
    hora_inicio: time
    hora_fin: time
   
class TurnoCreate(TurnoBase):
    id_escuela: Optional[int] = None
    pass

class TurnoUpdate(TurnoBase):
    nombre: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None

class TurnoResponse(TurnoBase):
    id: int
    id_escuela: int
    estado: int
    # Opcional: Ver los bloques dentro del turno bloques: List[BloqueHorarioResponse] = [] 
    class Config:
        from_attributes = True


# --- Esquemas de Bloque Horario ---
class BloqueHorarioBase(BaseModel):
    dia_semana: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    orden: Optional[int] = None
    id_turno: Optional[int] = None
    estado: Optional[int] = None


class BloqueHorarioCreate(BloqueHorarioBase):
    pass

class BloqueHorarioResponse(BloqueHorarioBase):
    id: int
    estado: int
    class Config:
        from_attributes = True

