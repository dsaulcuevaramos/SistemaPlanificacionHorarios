from sqlalchemy import Column, String, Integer
from app.models.base import Base, BaseMixin

class Catalogo(Base, BaseMixin):
    
    nombre_tabla = Column(String(50), nullable=False)
    codigo = Column(String(20), nullable=False)
    descripcion = Column(String(100), nullable=False)
    orden = Column(Integer, nullable=True)