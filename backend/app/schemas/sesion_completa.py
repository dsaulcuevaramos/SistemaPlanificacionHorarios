from pydantic import BaseModel
from typing import Optional

# 1. Esquemas Base (Hojas del árbol)
class CursoSimple(BaseModel):
    id: int
    nombre: str
    ciclo: int
    codigo: str
    class Config:
        from_attributes = True

class CursoAperturadoSimple(BaseModel):
    id: int
    curso: CursoSimple
    class Config:
        from_attributes = True

class DocenteSimple(BaseModel):
    id: int
    nombre: str
    apellido: str
    class Config:
        from_attributes = True

class GrupoSimple(BaseModel):
    id: int
    nombre: str
    id_turno: int
    curso_aperturado: CursoAperturadoSimple
    docente: Optional[DocenteSimple] = None
    class Config:
        from_attributes = True

# 2. El Schema Principal que usaremos en el Endpoint
class SesionFullResponse(BaseModel):
    id: int
    tipo_sesion: str
    duracion_horas: int
    id_grupo: int
    grupo: GrupoSimple  # <--- ¡ESTO ES LO IMPORTANTE!
    
    class Config:
        from_attributes = True