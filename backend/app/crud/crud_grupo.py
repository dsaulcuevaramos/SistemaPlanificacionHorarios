from app.crud.base import CRUDBase
from app.models.grupo import Grupo
from app.schemas.grupo import GrupoCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

class CRUDGrupo(CRUDBase[Grupo, GrupoCreate, GrupoCreate]):
    async def get_by_periodo(self, db: AsyncSession, id_periodo: int):
        """Obtiene grupos de un periodo específico con sus relaciones."""
        from app.models.curso_aperturado import CursoAperturado
        stmt = (
            select(self.model)
            .join(CursoAperturado)
            .where(CursoAperturado.id_periodo == id_periodo)
            .options(selectinload(Grupo.docente))
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    pass

grupo = CRUDGrupo(Grupo)