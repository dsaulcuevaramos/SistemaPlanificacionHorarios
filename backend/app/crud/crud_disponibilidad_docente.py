from app.crud.base import CRUDBase
from app.models.disponibilidad_docente import DisponibilidadDocente
from app.schemas.disponibilidad_docente import DisponibilidadDocenteCreate, DisponibilidadDocenteUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

class CRUDDisponibilidadDocente(CRUDBase[DisponibilidadDocente, DisponibilidadDocenteCreate, DisponibilidadDocenteUpdate]):
    
    async def get_by_periodo(self, db: AsyncSession, *, id_periodo: int) -> List[DisponibilidadDocente]:
        """Obtiene todos los registros de disponibilidad para un periodo específico."""
        stmt = select(self.model).where(self.model.id_periodo == id_periodo)
        result = await db.execute(stmt)
        return result.scalars().all()

disponibilidad_docente = CRUDDisponibilidadDocente(DisponibilidadDocente)