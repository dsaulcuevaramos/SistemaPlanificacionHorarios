# app/models/periodo_academico.py
from sqlalchemy import Column, String, Date
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class PeriodoAcademico(Base, BaseMixin):
    __tablename__ = 'periodo_academico'
    
    codigo = Column(String(20))
    nombre = Column(String(100))
    descripcion = Column(String(255))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    # Relaciones
    # Nota: Normalicé el nombre a 'cursos_aperturados' para coincidir con la clase CursoAperturado
    cursos_aperturados = relationship("CursoAperturado", back_populates="periodo")
    disponibilidades = relationship("DisponibilidadDocente", back_populates="periodo")
    horarios = relationship("Horario", back_populates="periodo")
    examenes = relationship("HorarioExamen", back_populates="periodo")

    