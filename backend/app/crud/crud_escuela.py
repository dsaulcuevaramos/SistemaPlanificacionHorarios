from app.crud.base import CRUDBase
from app.models.escuela import Escuela
from app.schemas.escuela import EscuelaCreate, EscuelaUpdate

class CRUDEscuela(CRUDBase[Escuela, EscuelaCreate, EscuelaUpdate]):
    pass

escuela = CRUDEscuela(Escuela)