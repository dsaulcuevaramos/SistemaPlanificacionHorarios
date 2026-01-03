# app/models/horario.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Horario(Base, BaseMixin):
    __tablename__ = 'horario'
    
    id_sesion = Column(Integer, ForeignKey('sesion.id'), nullable=False)
    id_bloque = Column(Integer, ForeignKey('bloque_horario.id'), nullable=False)
    id_aula = Column(Integer, ForeignKey('aula.id'), nullable=True)
    id_periodo = Column(Integer, ForeignKey('periodo_academico.id'), nullable=False)
    
    # Relaciones
    sesion = relationship("Sesion", back_populates="horarios")
    bloque_horario = relationship("BloqueHorario", back_populates="horarios")
    aula = relationship("Aula", back_populates="horarios")
    periodo = relationship("PeriodoAcademico", back_populates="horarios")