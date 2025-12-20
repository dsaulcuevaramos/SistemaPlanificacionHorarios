from typing import Optional
from datetime import date
from pydantic import BaseModel

class PlanVersionBase(BaseModel):
    codigo_version: str
    fecha_vigencia: date
    id_plan_estudio: int
    estado: int

class PlanVersionCreate(PlanVersionBase):
    pass

class PlanVersionUpdate(PlanVersionBase):
    codigo_version: Optional[str] = None
    fecha_vigencia: Optional[date] = None
    id_plan_estudio: Optional[int] = None
    estado: int
    
class PlanVersionResponse(PlanVersionBase):
    id: int
    estado: int

    class Config:
        from_attributes = True