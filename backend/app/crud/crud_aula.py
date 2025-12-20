from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.crud.base import CRUDBase
from app.models.aula import Aula
from app.schemas.aula import AulaCreate, AulaUpdate

class CRUDAula(CRUDBase[Aula, AulaCreate, AulaUpdate]):
    
    # Filtro Multi-tenant
    async def get_multi_by_escuela(
        self, db: AsyncSession, *, id_escuela: int, skip: int = 0, limit: int = 100
    ) -> List[Aula]:
        stmt = (
            select(self.model)
            .where(self.model.id_escuela == id_escuela)
            .offset(skip)
            .limit(limit)
        )
        if id_escuela is not None:
            stmt = stmt.where(self.model.id_escuela == id_escuela)

        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_con_relaciones(self, db: AsyncSession, *, id: int) -> Optional[Aula]:
        stmt = (
            select(self.model)
            .where(self.model.id == id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

aula = CRUDAula(Aula)