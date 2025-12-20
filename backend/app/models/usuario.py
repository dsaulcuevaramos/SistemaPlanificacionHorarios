# app/models/usuario.py
from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.models.base import Base, BaseMixin

class Usuario(Base, BaseMixin):
    # __tablename__ automático es 'usuario'
    
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))
    rol = Column(String(20))
    
    email = Column(String(100), unique=True, index=True, nullable=True)
    dni = Column(String(8), unique=True, index=True, nullable=True)
    
    # Lógica Multi-tenant
    id_escuela = Column(Integer, ForeignKey("escuela.id"), nullable=True)

    escuela = relationship("Escuela", back_populates="usuarios")

"""
class Usuario(Base, BaseMixin):
    __tablename__ = 'usuario'

    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False) # Almacena el hash
    rol = Column(String(20)) # ADMIN, SECRETARIA, etc.
    
    # FK de Multi-tenancy
    id_escuela = Column(Integer, ForeignKey('escuela.id'), nullable=True) #para admin será True, probar esta logica de usuario
    
    # Relación
    escuela = relationship("Escuela", back_populates="usuarios")
"""