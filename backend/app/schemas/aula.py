from typing import Optional, List
from pydantic import BaseModel, Field

class AulaBase(BaseModel):
    nombre: str
    pabellon: str
    aforo: int
    tipo_aula: str      # Ej: "LABORATORIO"
    recursos: List[str] # Pydantic convierte la lista a JSON automáticamente
    id_escuela: int
    piso: int

class AulaCreate(AulaBase):
    #id_escuela: int
    pass

class AulaUpdate(AulaBase):
    nombre: Optional[str] = None
    pabellon: Optional[str] = None
    aforo: Optional[int] = None
    tipo_aula: Optional[str] = None
    recursos: Optional[List[str]] = None
    id_escuela: Optional[int] = None
    estado: Optional[int] = None
    piso: Optional[int] = None
    
class AulaResponse(AulaBase):
    id: int
    estado: int
    
    class Config:
        from_attributes = True

class AulaListResponse(BaseModel):
    data: List[AulaResponse]