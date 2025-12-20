from pydantic import BaseModel
from typing import Optional

class SesionBase(BaseModel):
    tipo_sesion: str # TEORIA o PRACTICA 
    duracion_horas: int
    id_grupo: int

class SesionCreate(SesionBase):
    pass

class SesionResponse(SesionBase):
    id: int
    estado: int
    class Config:
        from_attributes = True