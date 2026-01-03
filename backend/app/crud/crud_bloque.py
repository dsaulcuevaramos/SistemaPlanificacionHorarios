from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.crud.base import CRUDBase
from app.models.bloque_horario import BloqueHorario
from app.schemas.bloque_horario import BloqueHorarioCreate
from sqlalchemy import case

class CRUDBloque(CRUDBase[BloqueHorario, BloqueHorarioCreate, BloqueHorarioCreate]):    
    
    async def get_by_turno(self, db: AsyncSession, id_turno: int) -> List[BloqueHorario]:

        orden_dias = case(
            {"Lunes": 1,"Martes": 2,"Miércoles": 3,"Jueves": 4,"Viernes": 5,"Sábado": 6,"Domingo": 7
            },value=self.model.dia_semana)
        
        """Obtiene todos los bloques de un turno ordenados por día y orden """
        stmt = select(self.model).where(
            self.model.id_turno == id_turno,
            self.model.estado == 1
        ).order_by(orden_dias, self.model.orden)

        
        result = await db.execute(stmt)
        return result.scalars().all()

    async def create_bulk(self, db: AsyncSession, id_turno: int, dias: List[str], intervalos: List):
        bloques_creados = []
        for dia in dias:
            for inv in intervalos:
                db_obj = BloqueHorario(
                    dia_semana=dia,
                    hora_inicio=inv.inicio, # Cambio: acceso a atributo del schema
                    hora_fin=inv.fin,       # Cambio: acceso a atributo del schema
                    orden=inv.orden,        # Cambio: acceso a atributo del schema
                    id_turno=id_turno,
                    estado=1
                )
                db.add(db_obj)
                bloques_creados.append(db_obj)
        
        await db.commit()
        return bloques_creados  
    
    async def remove_by_turno(self, db: AsyncSession, id_turno: int):
        """Elimina todos los bloques asociados a un turno específico[cite: 9, 10]."""
        stmt = delete(self.model).where(self.model.id_turno == id_turno)
        await db.execute(stmt)
        await db.commit()
        return True


    async def get_by_periodo_map(self, db: AsyncSession, id_periodo: int):
        """
        Retorna un diccionario {(dia, orden): id_bloque} para búsqueda rápida.
        Asume que los bloques están ligados al periodo a través del turno.
        """
        # Nota: Aquí deberás ajustar el join según si tu Periodo tiene Turnos o viceversa.
        # Ejemplo genérico asumiendo Turno -> Bloque
        stmt = (
            select(self.model)
            # .join(Turno) ... dependiendo de tu modelo
            # .where(Turno.id_periodo == id_periodo)
        )
        result = await db.execute(stmt)
        bloques = result.scalars().all()
        
        mapa = {}
        for b in bloques:
            # Normalizamos dia y orden
            mapa[(b.dia_semana, b.orden)] = b.id
        return mapa


bloque = CRUDBloque(BloqueHorario)
