from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

#from typing import TYPE_CHECKING
#from app.models.escuela import Escuela # Necesario para la relación multi-tenant

class Docente(Base, BaseMixin):
    # __tablename__ = 'docente'
    dni = Column(String(15), unique=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    email = Column(String(100))
    telefono = Column(String(20))
    tipo_docente = Column(String(20))
    horas_maximas_semanales = Column(Integer)
    
    id_escuela = Column(Integer, ForeignKey("escuela.id")) 
    
    # Relaciones
    escuela = relationship("Escuela", back_populates="docentes")
    contratos = relationship("ContratoDocente", back_populates="docente")
    disponibilidad = relationship("DisponibilidadDocente", back_populates="docente")
    grupos = relationship("Grupo", back_populates="docente")

    
"""
if TYPE_CHECKING:
    from .grupo import Grupo
    from .contrato_docente import ContratoDocente

class Docente(Base, BaseMixin):
    __tablename__ = 'docente'
    
    dni = Column(String(15), unique=True, index=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(100))
    telefono = Column(String(20))
    
    # Lógica de Catálogo (FK Lógica)
    tipo_docente = Column(String(20), nullable=False) 
    
    horas_maximas_semanales = Column(Integer)
    
    # Multi-tenancy (Seguridad)
    id_escuela = Column(Integer, ForeignKey('escuela.id'), nullable=False)
    
    # RELACIONES INVERSAS
    escuela = relationship("Escuela", back_populates="docentes") 
    grupos = relationship("Grupo", back_populates="docente")
    contratos = relationship("ContratoDocente", back_populates="docente")

    disponibilidades = relationship("DisponibilidadDocente", back_populates="docente")
"""