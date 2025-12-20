from app.crud.base import CRUDBase
from app.models.contrato_docente import ContratoDocente
from app.schemas.contrato_docente import ContratoDocenteCreate, ContratoDocenteUpdate
from sqlalchemy.future import select
from sqlalchemy import delete
from app.models.contrato_docente import ContratoDocente
from app.models.disponibilidad_docente import DisponibilidadDocente
from sqlalchemy.ext.asyncio import AsyncSession

class CRUDContratoDocente(CRUDBase[ContratoDocente, ContratoDocenteCreate, ContratoDocenteUpdate]):
    
    async def eliminar_contrato_completo(self, db: AsyncSession, *, id_docente: int, id_periodo: int):
        # Eliminamos de disponibilidad
        await db.execute(
            delete(DisponibilidadDocente).where(
                DisponibilidadDocente.id_docente == id_docente,
                DisponibilidadDocente.id_periodo == id_periodo
            )
        )
        # Eliminamos el contrato
        await db.execute(
            delete(ContratoDocente).where(ContratoDocente.id_docente == id_docente)
        )
        await db.commit()
        return True
    
    pass

contrato_docente = CRUDContratoDocente(ContratoDocente)