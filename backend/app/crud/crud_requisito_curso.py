# app/crud/requisito_curso.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.curso_requisito import RequisitoCurso
from app.schemas.curso import RequisitoCursoCreate

class CRUDRequisitoCurso:
    """Clase para manejar las operaciones CRUD de los prerrequisitos (Malla)."""

    async def create(
        self, 
        db: AsyncSession, 
        id_curso_dependiente: int, 
        obj_in: RequisitoCursoCreate
    ) -> RequisitoCurso:
        """Crea una nueva relación de prerrequisito (Edge)."""
        db_obj = RequisitoCurso(
            id_curso_dependiente=id_curso_dependiente,
            id_curso_requisito=obj_in.id_curso_requisito,
            tipo_requisito=obj_in.tipo_requisito
            # El campo estado usa su default (1)
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(
        self, 
        db: AsyncSession, 
        id_curso_dependiente: int, 
        id_curso_requisito: int
    ) -> bool:
        """Elimina una relación de prerrequisito específica (Desvincula)."""
        stmt = delete(RequisitoCurso).where(
            RequisitoCurso.id_curso_dependiente == id_curso_dependiente,
            RequisitoCurso.id_curso_requisito == id_curso_requisito
        )
        result = await db.execute(stmt)
        await db.commit()
        # Devuelve True si se eliminó al menos 1 fila
        return result.rowcount > 0

    async def get_by_course(
        self, 
        db: AsyncSession, 
        id_curso_dependiente: int
    ) -> list[RequisitoCurso]:
        """Obtiene todos los requisitos para un curso dependiente específico."""
        stmt = select(RequisitoCurso).where(
            RequisitoCurso.id_curso_dependiente == id_curso_dependiente
        )
        result = await db.execute(stmt)
        return result.scalars().all()

requisito_curso = CRUDRequisitoCurso()