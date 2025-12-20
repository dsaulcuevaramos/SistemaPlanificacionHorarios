from app.crud.base import CRUDBase
from app.models.bloque_horario import BloqueHorario
from app.schemas.bloque_horario import BloqueHorarioCreate
from app.models.bloque_horario import BloqueHorario
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

class CRUDBloque(CRUDBase[BloqueHorario, BloqueHorarioCreate, BloqueHorarioCreate]):
    # Implementa métodos de ordenamiento si es necesario
    
    async def get_by_turno(self, db: AsyncSession, id_turno: int):
        stmt = select(self.model).where(self.model.id_turno == id_turno).order_by(self.model.orden)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    pass

bloque = CRUDBloque(BloqueHorario)