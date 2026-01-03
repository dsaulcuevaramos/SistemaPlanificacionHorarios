from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from app.crud.base import CRUDBase
from app.models.sesion import Sesion
from app.models.grupo import Grupo
from app.models.curso_aperturado import CursoAperturado
from app.models.curso import Curso
from app.models.docente import Docente
from app.schemas.sesion import SesionCreate, SesionUpdate

class CRUDSesion(CRUDBase[Sesion, SesionCreate, SesionUpdate]):
    
    async def get_con_detalles(self, db: AsyncSession, id_sesion: int) -> Optional[Sesion]:
        """
        Obtiene la sesión con todas sus relaciones cargadas (Grupo, Docente, Curso)
        Vital para la validación de choques.
        """
        stmt = (
            select(Sesion)
            .options(
                joinedload(Sesion.grupo).joinedload(Grupo.docente),
                joinedload(Sesion.grupo).joinedload(Grupo.curso_aperturado).joinedload(CursoAperturado.curso)
            )
            .where(Sesion.id == id_sesion)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pendientes_export(self, db: AsyncSession, id_periodo: int) -> List[Sesion]:
        """
        Obtiene todas las sesiones del periodo para generar la plantilla CSV.
        """
        stmt = (
            select(Sesion)
            .join(Grupo)
            .join(CursoAperturado)
            .where(CursoAperturado.id_periodo == id_periodo)
            .options(
                joinedload(Sesion.grupo).joinedload(Grupo.curso_aperturado).joinedload(CursoAperturado.curso),
                joinedload(Sesion.grupo).joinedload(Grupo.docente)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().all()

sesion = CRUDSesion(Sesion)