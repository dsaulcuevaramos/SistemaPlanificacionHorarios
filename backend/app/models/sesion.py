# app/models/sesion.py
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Sesion(Base, BaseMixin):
    __tablename__ = 'sesion'
    
    tipo_sesion = Column(String(20)) 
    duracion_horas = Column(Integer)
    id_grupo = Column(Integer, ForeignKey('grupo.id'), nullable=False)
    
    # Relaciones
    grupo = relationship("Grupo", back_populates="sesiones")
    horarios = relationship("Horario", back_populates="sesion")