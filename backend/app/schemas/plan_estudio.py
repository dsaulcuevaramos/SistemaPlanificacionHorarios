from typing import Optional
from datetime import date
from pydantic import BaseModel

class PlanEstudioBase(BaseModel):
    codigo: str
    nombre: str
    anio_inicio: int
    id_escuela: int # Aquí SÍ es obligatorio, solo el SuperAdmin puede crear sin ID
    estado: int

class PlanEstudioCreate(PlanEstudioBase):
    pass

class PlanEstudioUpdate(PlanEstudioBase):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    anio_inicio: Optional[int] = None
    id_escuela: Optional[int] = None # No debería cambiarse, pero por flexibilidad
    estado: Optional[int] = None
    
class PlanEstudioResponse(PlanEstudioBase):
    id: int
    estado: int

    class Config:
        from_attributes = True