from typing import Optional
from pydantic import BaseModel

# Base común
class CatalogoBase(BaseModel):
    nombre_tabla: str
    codigo: str
    descripcion: str
    orden: Optional[int] = 0

# Para crear (mismos campos que base)
class CatalogoCreate(CatalogoBase):
    pass

# Para actualizar (todos opcionales)
class CatalogoUpdate(CatalogoBase):
    nombre_tabla: Optional[str] = None
    codigo: Optional[str] = None
    descripcion: Optional[str] = None

# Para leer (incluye ID y Estado)
class CatalogoResponse(CatalogoBase):
    id: int
    estado: int

    class Config:
        from_attributes = True # Antes orm_mode = True