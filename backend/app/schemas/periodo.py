from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class PeriodoBase(BaseModel):
    codigo: str
    nombre: str
    descripcion: Optional[str] = None
    fecha_inicio: date
    fecha_fin: date

class PeriodoCreate(PeriodoBase):
    pass

class PeriodoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    # El código usualmente no se edita para mantener integridad, pero depende de ti

class PeriodoResponse(PeriodoBase):
    id: int
    estado: int # Del BaseMixin (1=Activo, 0=Inactivo)
    
    class Config:
        model_config = ConfigDict(from_attributes=True) #############
        from_attributes = True