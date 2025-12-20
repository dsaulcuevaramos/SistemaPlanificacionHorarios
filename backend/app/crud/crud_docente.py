from app.crud.base import CRUDBase
from app.models.docente import Docente
from app.schemas.docente import DocenteCreate, DocenteUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

class CRUDDocente(CRUDBase[Docente, DocenteCreate, DocenteUpdate]):
    

    # Implementamos el filtro Multi-tenant para listar
    async def get_multi_by_escuela(
        self, db: AsyncSession, *, id_escuela: int, skip: int = 0, limit: int = 100
    ) -> List[Docente]:
        """Obtiene la lista de docentes filtrada por ID de escuela, cargando las relaciones."""
        stmt = (
            select(self.model)
            .where(self.model.id_escuela == id_escuela)
            .offset(skip)
            .limit(limit)
            # CRÍTICO: CARGA ANSIOSA (EAGER LOADING)  se agrea esto de options 
            .options(
                selectinload(Docente.contratos),
                selectinload(Docente.disponibilidad) # Asumiendo que la incluiste en el esquema de respuesta
            )
        )
        # Aplicar el filtro si no es None
        if id_escuela is not None:
            stmt = stmt.where(self.model.id_escuela == id_escuela)

        result = await db.execute(stmt)
        return result.scalars().unique().all()
    
    async def get_by_dni(self, db: AsyncSession, dni: str) -> Optional[Docente]:
        """Obtiene un docente por su número de DNI."""
        stmt = select(self.model).where(self.model.dni == dni)
        result = await db.execute(stmt)
        return result.scalars().first()
    

    async def get_with_relations(self, db: AsyncSession, *, id: int) -> Optional[Docente]:
        """Obtiene un docente por ID con sus relaciones precargadas."""
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(Docente.contratos),
                selectinload(Docente.disponibilidad)
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

docente = CRUDDocente(Docente)