from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin
from sqlalchemy.dialects.postgresql import JSONB

class Aula(Base, BaseMixin):
   # __tablename__ = 'aula'
    nombre = Column(String(50))
    pabellon = Column(String(20))
    aforo = Column(Integer)
    tipo_aula = Column(String(20))
    recursos = Column(JSON, nullable=False, default=[]) 
    piso = Column(Integer)
    
    id_escuela = Column(Integer, ForeignKey("escuela.id"))
    
    # Relaciones
    escuela = relationship("Escuela", back_populates="aulas")
    horarios = relationship("Horario", back_populates="aula")
    examenes_agendados = relationship("HorarioExamen", back_populates="aula")

"""
class Aula(Base, BaseMixin):
    __tablename__ = 'aula'
    
    nombre = Column(String(50), nullable=False)
    pabellon = Column(String(20))
    aforo = Column(Integer)
    
    tipo_aula = Column(String(20)) # Lógica -> catalogo
    recursos = Column(JSON) # Para guardar la lista de recursos [Proyector, Aire]
    
    # Multi-tenancy
    id_escuela = Column(Integer, ForeignKey('escuela.id'), nullable=False)
    
    # Relaciones inversas
    escuela = relationship("Escuela", back_populates="aulas") 
    
    # (El resto de las relaciones de horario irían aquí)
    horarios = relationship("Horario", back_populates="aula")
    examenes_agendados = relationship("HorarioExamen", back_populates="aula")
"""  