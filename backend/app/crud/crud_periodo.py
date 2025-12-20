from app.crud.base import CRUDBase
from app.models.periodo_academico import PeriodoAcademico
from app.schemas.periodo import PeriodoCreate, PeriodoUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

class CRUDPeriodo (CRUDBase[PeriodoAcademico, PeriodoCreate, PeriodoUpdate]):


    async def get_by_codigo(self, db: AsyncSession, codigo: str) -> Optional[PeriodoAcademico]:
        stmt = select(PeriodoAcademico).where(PeriodoAcademico.codigo == codigo)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    
    pass

periodo = CRUDPeriodo(PeriodoAcademico)