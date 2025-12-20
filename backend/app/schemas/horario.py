from pydantic import BaseModel

class HorarioBase(BaseModel):
    id_sesion: int
    id_bloque: int
    id_aula: int
    id_periodo: int

class HorarioCreate(HorarioBase):
    pass

class HorarioResponse(HorarioBase):
    id: int
    estado: int
    class Config:
        from_attributes = True