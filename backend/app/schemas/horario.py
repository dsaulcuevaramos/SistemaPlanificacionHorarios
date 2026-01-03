from typing import Optional
from pydantic import BaseModel

from app.schemas.sesion_completa import SesionFullResponse 
from app.schemas.bloque_horario import BloqueHorarioResponse

class HorarioBase(BaseModel):
    id_sesion: int
    id_bloque: int
    id_aula: Optional[int] = None
    id_periodo: int

class HorarioCreate(HorarioBase):
    pass

class HorarioUpdate(BaseModel):
    id_sesion: Optional[int] = None
    id_bloque: Optional[int] = None
    id_aula: Optional[int] = None
    id_periodo: Optional[int] = None
    estado: Optional[int] = None


class HorarioResponse(HorarioBase):
    id: int
    estado: int

    sesion: Optional[SesionFullResponse] = None
    bloque_horario: Optional[BloqueHorarioResponse] = None

    class Config:
        from_attributes = True
        
