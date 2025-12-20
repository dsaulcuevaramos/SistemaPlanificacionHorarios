# app/models/escuela.py
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Escuela(Base, BaseMixin):
    # No necesitamos definir __tablename__, lo hace automático (será 'escuela')
    nombre = Column(String(100))
    facultad = Column(String(100))

    # Relaciones
    usuarios = relationship("Usuario", back_populates="escuela")
    planes_estudio = relationship("PlanEstudio", back_populates="escuela")
    docentes = relationship("Docente", back_populates="escuela")
    aulas = relationship("Aula", back_populates="escuela")
    turnos = relationship("Turno", back_populates="escuela", cascade="all, delete-orphan")


"""
class Escuela(Base, BaseMixin):
    __tablename__ = 'escuela' # Nombre de la tabla en BD

    nombre = Column(String(100), nullable=False)
    facultad = Column(String(100))
    
    # Relaciones inversas (para multi-tenancy)
    usuarios = relationship("Usuario", back_populates="escuela") 
    planes = relationship("PlanEstudio", back_populates="escuela")
    docentes = relationship("Docente", back_populates="escuela") 
    aulas = relationship("Aula", back_populates="escuela")
"""
