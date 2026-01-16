# app/models/horario.py
from sqlalchemy import Column, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Horario(Base, BaseMixin):
    __tablename__ = 'horario'
    
    id_sesion = Column(Integer, ForeignKey('sesion.id'), nullable=False)
    id_bloque = Column(Integer, ForeignKey('bloque_horario.id'), nullable=False)
    id_aula = Column(Integer, ForeignKey('aula.id'), nullable=True)
    id_periodo = Column(Integer, ForeignKey('periodo_academico.id'), nullable=False)
    
    ciclo = Column(Integer, nullable=False, default=0)
    grupo = Column(String(50), nullable=False, default='-')

    # Relaciones
    sesion = relationship("Sesion", back_populates="horarios")
    bloque_horario = relationship("BloqueHorario", back_populates="horarios")
    aula = relationship("Aula", back_populates="horarios")
    periodo = relationship("PeriodoAcademico", back_populates="horarios")


    __table_args__ = (
        UniqueConstraint('id_periodo', 'id_bloque', 'ciclo', 'grupo', name='uq_horario_casilla'),
    )