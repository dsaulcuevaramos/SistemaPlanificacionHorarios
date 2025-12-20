from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class PlanVersion(Base, BaseMixin):
    __tablename__ = 'plan_version'

    codigo_version = Column(String(30))
    fecha_vigencia = Column(Date)
    
    id_plan_estudio = Column(Integer, ForeignKey("plan_estudio.id"))

    # Relaciones
    plan_estudio = relationship("PlanEstudio", back_populates="versiones")
    cursos = relationship("Curso", back_populates="plan_version")