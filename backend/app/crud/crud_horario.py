from app.crud.base import CRUDBase
from app.models.horario import Horario
from app.models.sesion import Sesion
from app.models.grupo import Grupo
from app.models.curso_aperturado import CursoAperturado
from app.schemas.horario import HorarioCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload, joinedload

class CRUDHorario(CRUDBase[Horario, HorarioCreate, HorarioCreate]):
    async def get_horario_periodo(self, db: AsyncSession, id_periodo: int):
        """Obtiene todo el horario de un periodo con relaciones cargadas."""
        stmt = (
            select(self.model)
            .where(self.model.id_periodo == id_periodo)
            .options(
                # Cargamos la sesión y TODA su cadena hasta el curso para saber el ciclo
                joinedload(Horario.sesion)
                    .joinedload(Sesion.grupo)
                    .joinedload(Grupo.curso_aperturado)
                    .joinedload(CursoAperturado.curso),
                selectinload(Horario.bloque),
                selectinload(Horario.aula)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    pass

horario = CRUDHorario(Horario)