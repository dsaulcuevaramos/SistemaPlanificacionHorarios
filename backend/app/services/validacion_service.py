from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.horario import Horario
from app.models.sesion import Sesion
from app.models.grupo import Grupo
from app.models.restriccion import Restriccion

class ValidacionService:
    
    async def _check_regla_activa(self, db: AsyncSession, tipo_regla: str) -> bool:
        """Verifica si una regla global está activa en la BD"""
        stmt = select(Restriccion).where(
            and_(
                Restriccion.tipo == tipo_regla,
                Restriccion.entidad_referencia == 'SISTEMA',
                Restriccion.estado == 1
            )
        )
        result = await db.execute(stmt)
        regla = result.scalars().first()
        return regla is not None

    async def validar_movimiento(
        self, 
        db: AsyncSession, 
        id_sesion: int, 
        id_bloque: int, 
        id_aula: int, 
        id_periodo: int
    ):
        errores = []

        stmt_sesion = select(Sesion).where(Sesion.id == id_sesion)
        sesion = (await db.execute(stmt_sesion)).scalars().first()
        
        if not sesion: return ["Sesión no encontrada"]
        
        # --- VALIDACIÓN NUEVA: CONTROL DE HORAS (TETRIS) ---
        # Contamos cuántos bloques ya tiene asignada esta sesión en la BD
        stmt_conteo = select(func.count(Horario.id)).where(
            and_(
                Horario.id_sesion == id_sesion,
                Horario.id_periodo == id_periodo,
                Horario.id_bloque != id_bloque # Excluir el bloque actual si es una edición (mover)
            )
        )
        horas_asignadas = (await db.execute(stmt_conteo)).scalar()
        
        # Si la sesión tiene duracion 4 horas, y ya hay 4 asignadas, no dejar meter otra.
        if horas_asignadas >= sesion.duracion_horas:
            errores.append(f"LIMITE_HORAS: Esta sesión ya completó sus {sesion.duracion_horas} horas.")


        # 1. Obtener datos de la sesión
        stmt_sesion = select(Sesion).where(Sesion.id == id_sesion)
        sesion = (await db.execute(stmt_sesion)).scalars().first()
        
        if not sesion:
            return ["Sesión no encontrada"]

        stmt_grupo = select(Grupo).where(Grupo.id == sesion.id_grupo)
        grupo = (await db.execute(stmt_grupo)).scalars().first()
        
        id_docente = grupo.id_docente
        id_grupo = grupo.id

        # --- VALIDACIÓN 1: CRUCE DE DOCENTE ---
        if await self._check_regla_activa(db, 'CRUCE_DOCENTE'):
            if id_docente:
                stmt_cruce_doc = (
                    select(Horario)
                    .join(Sesion)
                    .join(Grupo)
                    .where(
                        and_(
                            Horario.id_bloque == id_bloque,
                            Horario.id_periodo == id_periodo,
                            Grupo.id_docente == id_docente,
                            Horario.id_sesion != id_sesion 
                        )
                    )
                )
                cruce_doc = (await db.execute(stmt_cruce_doc)).scalars().first()
                if cruce_doc:
                    errores.append(f"CRUCE_DOCENTE: El docente ya tiene clase asignada en este bloque.")

        # --- VALIDACIÓN 2: CRUCE DE AULA ---
        if await self._check_regla_activa(db, 'CRUCE_AULA'):
            if id_aula:
                stmt_cruce_aula = (
                    select(Horario)
                    .where(
                        and_(
                            Horario.id_bloque == id_bloque,
                            Horario.id_periodo == id_periodo,
                            Horario.id_aula == id_aula,
                            Horario.id_sesion != id_sesion
                        )
                    )
                )
                cruce_aula = (await db.execute(stmt_cruce_aula)).scalars().first()
                if cruce_aula:
                    errores.append(f"CRUCE_AULA: El aula ya está ocupada en este bloque.")

        # --- VALIDACIÓN 3: CRUCE DE GRUPO ---
        if await self._check_regla_activa(db, 'CRUCE_GRUPO'):
            stmt_cruce_grupo = (
                select(Horario)
                .join(Sesion)
                .where(
                    and_(
                        Horario.id_bloque == id_bloque,
                        Horario.id_periodo == id_periodo,
                        Sesion.id_grupo == id_grupo,
                        Horario.id_sesion != id_sesion
                    )
                )
            )
            cruce_grupo = (await db.execute(stmt_cruce_grupo)).scalars().first()
            if cruce_grupo:
                errores.append(f"CRUCE_GRUPO: El grupo estudiantil ya tiene clase.")

        return errores