from app.crud.base import CRUDBase
from app.models.plan_version import PlanVersion
from app.schemas.plan_version import PlanVersionCreate, PlanVersionUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

class CRUDPlanVersion(CRUDBase[PlanVersion, PlanVersionCreate, PlanVersionUpdate]):
    # Por ahora, CRUDBase genérico es suficiente
    pass

    async def get_multi_by_escuela(
        self, db: AsyncSession, *, id_escuela: Optional[int], skip: int = 0, limit: int = 100
    ) -> List[PlanVersion]:
        
        stmt = (
            select(self.model)
            .options(
                # CRÍTICO: Cargar la relación con el Plan Principal si el esquema lo requiere
                selectinload(PlanVersion.plan) 
            )
            .offset(skip)
            .limit(limit)
        )
        
        # Aplicar el filtro por id_escuela si no es None
        if id_escuela is not None:
            # CRÍTICO: Filtrar por la escuela del usuario
            stmt = stmt.where(self.model.id_escuela == id_escuela) 

        result = await db.execute(stmt)
        return result.scalars().unique().all()

plan_version = CRUDPlanVersion(PlanVersion)