# app/models/grupo.py
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin
from app.models.docente import Docente 
from app.models.turno import Turno 
from app.models.curso_aperturado import CursoAperturado # Asumiendo este modelo

class Grupo(Base, BaseMixin):
    __tablename__ = 'grupo'
    
    nombre = Column(String(30), nullable=False)
    vacantes = Column(Integer)
    
    id_curso_aperturado = Column(Integer, ForeignKey('curso_aperturado.id'), nullable=False)
    id_docente = Column(Integer, ForeignKey('docente.id'), nullable=True) 
    id_turno = Column(Integer, ForeignKey('turno.id'), nullable=False) 
    
    # Relaciones
    curso_aperturado = relationship("CursoAperturado", back_populates="grupos")
    docente = relationship("Docente", back_populates="grupos")
    turno = relationship("Turno", back_populates="grupos")
    sesiones = relationship("Sesion", back_populates="grupo")
    examenes = relationship("HorarioExamen", back_populates="grupo")