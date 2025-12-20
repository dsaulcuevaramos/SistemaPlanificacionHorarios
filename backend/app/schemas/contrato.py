from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContratoYDisponibilidadCreate(BaseModel):
    id_docente: int
    id_periodo: int
    fecha_inicio: date
    fecha_fin: date
    horas_tope_semanales: int
    turnos_preferidos: str