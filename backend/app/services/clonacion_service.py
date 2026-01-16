from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Importa tus modelos
from app.models.curso_aperturado import CursoAperturado
from app.models.grupo import Grupo
from app.models.sesion import Sesion
from app.models.disponibilidad_docente import DisponibilidadDocente

# Importa tu función auxiliar de actualización (la que estaba en grupos.py)
# Asumo que la moverás a un lugar común o la importarás desde ahí.
# Si está en crud/grupos.py o routers/grupos.py, ajusta este import.
from app.api.endpoints.grupos import actualizar_disponibilidad_docente 

async def clonar_carga_academica(db: AsyncSession, id_periodo_origen: int, id_periodo_destino: int):
    """
    Clona toda la estructura académica (Cursos -> Grupos -> Sesiones) 
    de un periodo a otro.
    """
    
    # 1. Verificar que el destino esté vacío (Seguridad para no duplicar)
    check_stmt = select(CursoAperturado).where(CursoAperturado.id_periodo == id_periodo_destino).limit(1)
    if (await db.execute(check_stmt)).scalar():
        return {"status": "error", "message": "El periodo destino ya tiene cursos. Limpiálo antes de clonar."}

    # 2. Cargar TODA la data del origen (Optimizada con selectinload)
    stmt = (
        select(CursoAperturado)
        .where(CursoAperturado.id_periodo == id_periodo_origen)
        .options(
            selectinload(CursoAperturado.grupos).selectinload(Grupo.sesiones)
        )
    )
    cursos_origen = (await db.execute(stmt)).scalars().all()

    if not cursos_origen:
        return {"status": "error", "message": "El periodo origen no tiene cursos para clonar."}

    nuevos_objetos = []
    docentes_afectados = set()

    # 3. El Loop de la Clonación
    for curso_old in cursos_origen:
        # A. Crear Curso Aperturado Nuevo
        curso_new = CursoAperturado(
            id_curso=curso_old.id_curso,
            id_periodo=id_periodo_destino, # <--- Cambio clave
            cupos_proyectados=curso_old.cupos_proyectados
            # estado=1 (por defecto en tu modelo mixin)
        )
        db.add(curso_new)
        await db.flush() # Necesario para obtener el nuevo ID (curso_new.id)

        for grupo_old in curso_old.grupos:
            # B. Crear Grupo Nuevo
            grupo_new = Grupo(
                nombre=grupo_old.nombre,
                vacantes=grupo_old.vacantes,
                id_curso_aperturado=curso_new.id, # <--- Enlazamos al padre nuevo
                id_docente=grupo_old.id_docente,  # Clonamos al mismo profe
                id_turno=grupo_old.id_turno
            )
            db.add(grupo_new)
            await db.flush() # Obtenemos ID del grupo nuevo

            # Guardamos el docente para recalcular sus horas luego
            if grupo_new.id_docente:
                docentes_afectados.add(grupo_new.id_docente)

            for sesion_old in grupo_old.sesiones:
                # C. Crear Sesión Nueva
                sesion_new = Sesion(
                    tipo_sesion=sesion_old.tipo_sesion,
                    duracion_horas=sesion_old.duracion_horas,
                    id_grupo=grupo_new.id, # <--- Enlazamos al grupo nuevo
                    estado=1 
                )
                db.add(sesion_new)
    
    # 4. Confirmar Cambios en BD
    await db.commit()

    # 5. Recalcular Disponibilidad (Opcional pero recomendado)
    # Esto asegura que la tabla 'disponibilidad_docente' del nuevo periodo 
    # tenga las horas sumadas correctamente.
    for id_docente in docentes_afectados:
        # Debemos asegurarnos de crear la fila de disponibilidad para el nuevo periodo primero
        # o dejar que tu función 'actualizar_disponibilidad' la cree si no existe.
        await actualizar_disponibilidad_docente(db, id_docente, id_periodo_destino)
    
    await db.commit()

    return {"status": "success", "message": f"Se clonaron {len(cursos_origen)} cursos exitosamente."}