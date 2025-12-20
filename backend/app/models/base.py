from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import Column, Integer

@as_declarative()
class Base:
    """
    Clase base de la cual todos los modelos heredan.
    Sirve para la metadata de SQLAlchemy.
    """
    id: Any
    __name__: str

    # Genera automáticamente el nombre de la tabla en minúsculas
    # Ej: Clase 'TipoDocente' -> tabla 'tipodocente' (o puedes forzar snake_case)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

class BaseMixin:
    """
    Mixin para campos comunes.
    Evita repetir id y estado en cada modelo.
    """
    id = Column(Integer, primary_key=True, index=True)
    estado = Column(Integer, default=1, nullable=False)