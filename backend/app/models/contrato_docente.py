from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class ContratoDocente(Base, BaseMixin):
    __tablename__ = "contrato_docente"

    id_docente = Column(Integer, ForeignKey("docente.id"))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    horas_tope_semanales = Column(Integer, nullable=True)
    turnos_preferidos = Column(String(50))

    # Relaciones
    docente = relationship("Docente", back_populates="contratos")
