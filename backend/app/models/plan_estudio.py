from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class PlanEstudio(Base, BaseMixin):
    __tablename__ = 'plan_estudio'

    codigo = Column(String(20)) 
    nombre = Column(String(100))
    anio_inicio = Column(Integer)
    
    id_escuela = Column(Integer, ForeignKey("escuela.id"))
    
    # Relaciones
    escuela = relationship("Escuela", back_populates="planes_estudio")
    versiones = relationship("PlanVersion", back_populates="plan_estudio")