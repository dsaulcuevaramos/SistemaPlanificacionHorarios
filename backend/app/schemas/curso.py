from typing import Optional, List
from pydantic import BaseModel

class CursoBase(BaseModel):
    codigo: str
    nombre: str
    ciclo: int
    paridad: str         # Ej: PAR, IMPAR
    creditos: int
    horas_teoricas: int
    horas_practicas: int
    tipo_curso: str      # Ej: GENERAL, ESPECIFICO (ref. Catalogo)
    id_plan_version: int

class CursoCreate(CursoBase):
    pass

class CursoUpdate(CursoBase):
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    ciclo: Optional[int] = None
    paridad: Optional[str] = None
    creditos: Optional[int] = None
    horas_teoricas: Optional[int] = None
    horas_practicas: Optional[int] = None
    tipo_curso: Optional[str] = None
    id_plan_version: Optional[int] = None
    estado: Optional[int] = None

class CursoRequisitoInfo(BaseModel):
    id: int
    nombre: str
    codigo: str
    
    class Config:
        from_attributes = True

class CursoResponse(CursoBase):
    id: int
    estado: int

    requisitos: List[CursoRequisitoInfo] = []
    
    class Config:
        from_attributes = True


