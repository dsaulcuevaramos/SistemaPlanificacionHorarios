from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Restriccion(Base, BaseMixin):
    __tablename__ = 'restriccion'
    
    tipo = Column(String(50), nullable=False) # Ej: CRUCE_DOCENTE
    entidad_referencia = Column(String(50), nullable=False) # Ej: SISTEMA, DOCENTE, AULA
    id_entidad = Column(Integer, nullable=False) # ID específico si aplica
    
    # Regla en JSON para flexibilidad. 
    # Ej: {"dia": "Lunes", "bloque_inicio": 1, "bloque_fin": 4}
    # Ej para Sesion: {"horas_asignadas": 0, "horas_totales": 2}
    regla_json = Column(JSON, nullable=True)# Configuración extra
    
    peso = Column(Integer, default=100) # 100 = Hard (Error), <100 = Soft (Warning)
    estado = Column(Integer, default=1)

    id_periodo = Column(Integer, ForeignKey('periodo_academico.id'), nullable=True)