from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class BloqueHorario(Base, BaseMixin):
    __tablename__ = "bloque_horario"

    dia_semana = Column(String(15))
    hora_inicio = Column(Time)
    hora_fin = Column(Time)
    orden = Column(Integer)
    
    id_turno = Column(Integer, ForeignKey("turno.id"))
    
    # Relaciones
    turno = relationship("Turno", back_populates="bloques")
    horarios = relationship("Horario", back_populates="bloque_horario")