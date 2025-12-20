from app.crud.base import CRUDBase
from app.models.catalogo import Catalogo
from app.schemas.catalogo import CatalogoCreate, CatalogoUpdate

class CRUDCatalogo(CRUDBase[Catalogo, CatalogoCreate, CatalogoUpdate]):
    pass
    # Si necesitaras una consulta especial (ej: buscar por codigo), la agregas aquí:
    # async def get_by_codigo(self, db: AsyncSession, codigo: str):
    #     ...

catalogo = CRUDCatalogo(Catalogo)