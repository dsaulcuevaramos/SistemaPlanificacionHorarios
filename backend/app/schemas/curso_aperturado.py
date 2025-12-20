from pydantic import BaseModel
from typing import List, Optional

# Base
class CursoAperturadoBase(BaseModel):
    cupos_proyectados: int = 40 

# Para Crear (Individual, usado internamente)
class CursoAperturadoCreate(CursoAperturadoBase):
    id_curso: int
    id_periodo: int

# Para Responder (Lo que devuelve la API al listar)
class CursoAperturadoResponse(CursoAperturadoBase):
    id: int
    id_curso: int
    id_periodo: int
    
    class Config:
        from_attributes = True

# Para recibir del Frontend (El JSON que manda Vue)
class AperturaMasivaRequest(BaseModel):
    id_periodo: int
    ids_cursos: List[int] 
    cupos_general: int = 40