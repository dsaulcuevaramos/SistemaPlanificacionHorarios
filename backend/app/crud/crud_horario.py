from app.crud.base import CRUDBase
from app.models.horario import Horario
from app.schemas.horario import HorarioCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

class CRUDHorario(CRUDBase[Horario, HorarioCreate, HorarioCreate]):
    async def get_horario_periodo(self, db: AsyncSession, id_periodo: int):
        """Obtiene todo el horario de un periodo con relaciones cargadas."""
        stmt = (
            select(self.model)
            .where(self.model.id_periodo == id_periodo)
            .options(
                selectinload(Horario.sesion),
                selectinload(Horario.bloque),
                selectinload(Horario.aula)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    pass

horario = CRUDHorario(Horario)