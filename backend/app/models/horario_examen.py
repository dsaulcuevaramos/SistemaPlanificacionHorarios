# app/models/horario_examen.py
from sqlalchemy import Column, Integer, ForeignKey, Date, Time, String
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class HorarioExamen(Base, BaseMixin):
    __tablename__ = 'horario_examen'
    
    fecha = Column(Date, nullable=False)
    hora_inicio = Column(Time)
    hora_fin = Column(Time)
    tipo_examen = Column(String(20))
    
    id_curso_aperturado = Column(Integer, ForeignKey('curso_aperturado.id'), nullable=False)
    id_grupo = Column(Integer, ForeignKey('grupo.id'), nullable=True) 
    id_aula = Column(Integer, ForeignKey('aula.id'), nullable=False)
    id_periodo = Column(Integer, ForeignKey('periodo_academico.id'), nullable=False)
    
    # Relaciones
    curso_aperturado = relationship("CursoAperturado", back_populates="examenes")
    grupo = relationship("Grupo", back_populates="examenes")
    aula = relationship("Aula", back_populates="examenes_agendados")
    periodo = relationship("PeriodoAcademico", back_populates="examenes")
