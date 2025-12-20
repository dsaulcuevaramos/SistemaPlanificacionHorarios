# app/models/curso_aperturado.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin
from app.models.curso import Curso
from app.models.periodo_academico import PeriodoAcademico

class CursoAperturado(Base, BaseMixin):
    __tablename__ = 'curso_aperturado'
    
    id_curso = Column(Integer, ForeignKey('curso.id'), nullable=False)
    id_periodo = Column(Integer, ForeignKey('periodo_academico.id'), nullable=False)
    cupos_proyectados = Column(Integer)
    
    # Relaciones
    curso = relationship("Curso", back_populates="aperturas")
    periodo = relationship("PeriodoAcademico", back_populates="cursos_aperturados")
    grupos = relationship("Grupo", back_populates="curso_aperturado")
    examenes = relationship("HorarioExamen", back_populates="curso_aperturado")