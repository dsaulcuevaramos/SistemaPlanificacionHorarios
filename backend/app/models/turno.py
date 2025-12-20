from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Turno(Base, BaseMixin):
    # __tablename__ = 'turno'
    nombre = Column(String(50))
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    
    id_escuela = Column(Integer, ForeignKey("escuela.id"))
    
    # Relaciones
    escuela = relationship("Escuela", back_populates="turnos")
    grupos = relationship("Grupo", back_populates="turno")
    bloques = relationship("BloqueHorario", back_populates="turno")