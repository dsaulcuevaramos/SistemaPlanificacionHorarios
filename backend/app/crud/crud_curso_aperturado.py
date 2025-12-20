from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.crud.base import CRUDBase
from app.models.curso_aperturado import CursoAperturado
from app.schemas.curso_aperturado import CursoAperturadoCreate, CursoAperturadoResponse

class CRUDCursoAperturado(CRUDBase[CursoAperturado, CursoAperturadoCreate, CursoAperturadoCreate]):
    
    # Obtener cursos de un periodo
    async def get_by_periodo(self, db: AsyncSession, id_periodo: int) -> List[CursoAperturado]:
        stmt = select(self.model).where(self.model.id_periodo == id_periodo)
        result = await db.execute(stmt)
        return result.scalars().all()

    # Guardar múltiples cursos a la vez
    async def create_multi(self, db: AsyncSession, *, objs_in: List[CursoAperturadoCreate]) -> int:
        count = 0
        for obj_in in objs_in:
            # Convertimos esquema a dict para guardar
            obj_in_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in.model_dump()
            db_obj = self.model(**obj_in_data)
            db.add(db_obj)
            count += 1
        
        await db.commit()
        return count

# Instancia exportada para usar en el router
curso_aperturado = CRUDCursoAperturado(CursoAperturado)