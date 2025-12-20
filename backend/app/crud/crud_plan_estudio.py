from app.crud.base import CRUDBase
from app.models.plan_estudio import PlanEstudio
from app.schemas.plan_estudio import PlanEstudioCreate, PlanEstudioUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class CRUDPlanEstudio(CRUDBase[PlanEstudio, PlanEstudioCreate, PlanEstudioUpdate]):
    
    # Implementamos el filtro Multi-tenant para listar esto es segun el usuario logueado
    async def get_multi_by_escuela(
        self, db: AsyncSession, *, id_escuela: int, skip: int = 0, limit: int = 100
    ):
        stmt = (
            select(self.model)
            .where(self.model.id_escuela == id_escuela)
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

plan_estudio = CRUDPlanEstudio(PlanEstudio)