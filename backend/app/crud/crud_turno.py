from typing import List, Optional
from app.crud.base import CRUDBase
from app.models.turno import Turno
from app.schemas.turno import TurnoCreate, TurnoBase, TurnoResponse # Usamos TurnoBase como Update genérico por ahora
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

class CRUDTurno(CRUDBase[Turno, TurnoCreate, TurnoBase]):
    async def get(self, db: AsyncSession, id: int) -> Optional[Turno]:
        result = await db.execute(select(Turno).where(Turno.id == id))
        return result.scalars().first()

    async def get_multi_by_version(self, db: AsyncSession, version_id: int) -> List[Turno]:
        # Traer todos los turnos de una versión
        result = await db.execute(select(Turno).where(Turno.version_id == version_id))
        return result.scalars().all()

    async def create(self, db: AsyncSession, obj_in: TurnoCreate) -> Turno:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, id: int) -> Optional[Turno]:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj

    async def get_multi_by_escuela(self, db: AsyncSession, id_escuela: int) -> List[Turno]:
        """Trae todos los turnos de la escuela."""
        stmt = select(self.model).where(self.model.id_escuela == id_escuela)
        result = await db.execute(stmt)
        return result.scalars().all()
    
turno = CRUDTurno(Turno)