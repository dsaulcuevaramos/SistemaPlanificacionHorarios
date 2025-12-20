from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class DisponibilidadDocente(Base, BaseMixin):
    __tablename__ = "disponibilidad_docente"

    id_docente = Column(Integer, ForeignKey("docente.id"))
    id_periodo = Column(Integer, ForeignKey("periodo_academico.id"))
    horas_asignadas_actuales = Column(Integer, default=0)

    # Relaciones
    docente = relationship("Docente", back_populates="disponibilidad")
    periodo = relationship("PeriodoAcademico", back_populates="disponibilidades")


"""
# Asume que Docente y PeriodoAcademico ya están definidos y son importables
from app.models.docente import Docente 
from app.models.periodo_academico import PeriodoAcademico

class DisponibilidadDocente(Base, BaseMixin):
    __tablename__ = 'disponibilidad_docente'
    
    # FK que vincula al Docente y al Periodo
    id_docente = Column(Integer, ForeignKey('docente.id'), nullable=False)
    id_periodo = Column(Integer, ForeignKey('periodo_academico.id'), nullable=False)
    
    horas_asignadas_actuales = Column(Integer, default=0)
    
    # RELACIONES
    docente = relationship("Docente", back_populates="disponibilidades")
    periodo = relationship("PeriodoAcademico", back_populates="disponibilidades")
    
    # Definir una clave compuesta única para evitar duplicados (Docente solo puede tener 1 entrada por Periodo)
    # __table_args__ = (UniqueConstraint('id_docente', 'id_periodo', name='_docente_periodo_uc'),)"""