from pydantic import BaseModel
from datetime import date
from typing import Optional, List

# ==========================================
# 1. ESQUEMAS BASE (Mapeo directo a Base de Datos)
# ==========================================

class ContratoDocenteBase(BaseModel):
    id_docente: int
    fecha_inicio: date
    fecha_fin: date
    horas_tope_semanales: Optional[int] = 20
    turnos_preferidos: Optional[str] = 'Mañana'

# Este es el que el CRUD estaba buscando y no encontraba
class ContratoDocenteCreate(ContratoDocenteBase):
    id_docente: int
    id_periodo: int
    horas_tope_semanales: int = 20
    turnos_preferidos: str = "MAÑANA" # Esto es informativo 
    
    # --- CAMPO NUEVO PARA RESTRICCIONES ---
    dias_no_disponibles: List[str] = [] # Ej: ["Lunes", "Martes"]
    pass 

class ContratoDocenteUpdate(BaseModel):
    fecha_inicio: Optional[date] = None
    fecha_fin: Optional[date] = None
    horas_tope_semanales: Optional[int] = None
    turnos_preferidos: Optional[str] = None

class ContratoDocenteResponse(ContratoDocenteBase):
    id: int
    class Config:
        from_attributes = True

# ==========================================
# 2. ESQUEMAS LÓGICOS (Para los Endpoints / Frontend)
# ==========================================

# Este es para el formulario "Contratar Docente" del Frontend
# Recibe id_periodo en lugar de fechas (el backend calcula las fechas)
class ContratoAsignacionCreate(BaseModel):
    id_docente: int
    id_periodo: int
    horas_tope_semanales: int = 20
    turnos_preferidos: str

# Este es para la funcionalidad "Traer del Ciclo Pasado"
class RenovacionMasivaRequest(BaseModel):
    id_periodo_anterior: int
    id_periodo_nuevo: int