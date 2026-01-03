from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.orm import joinedload

from importlib import import_module

from app.core.database import get_db
# Modelos
from app.models.horario import Horario
from app.models.sesion import Sesion
from app.models.grupo import Grupo
from app.models.bloque_horario import BloqueHorario
from app.models.restriccion import Restriccion
from app.models.periodo_academico import PeriodoAcademico
from app.models.curso_aperturado import CursoAperturado
# Schemas
# Asegúrate de importar SesionFullResponse donde lo hayas definido
from app.schemas.sesion_completa import SesionFullResponse
from app.schemas.horario import HorarioCreate, HorarioResponse
from app.schemas.bloque_horario import BloqueHorarioResponse, BloqueMasivoCreate
from app.schemas.sesion import SesionResponse

# CRUDs
from app.crud.crud_sesion import sesion as crud_sesion
from app.crud.crud_bloque import bloque as crud_bloque

router = APIRouter()

# =====================================================================
#  1. LÓGICA DE VALIDACIÓN (EL ÁRBITRO)
# =====================================================================

async def validar_reglas_asignacion(
    db: AsyncSession, 
    id_sesion: int, 
    id_bloque: int, 
    id_periodo: int,
    id_aula: Optional[int] = None
) -> Optional[str]:
    """
    Verifica TODAS las reglas antes de permitir guardar un horario.
    Retorna None si es válido, o un string con el error.
    """
    
    # A. Datos de la Sesión
    stmt_sesion = select(Sesion).options(joinedload(Sesion.grupo)).where(Sesion.id == id_sesion)
    result_sesion = await db.execute(stmt_sesion)
    sesion_obj = result_sesion.scalar_one_or_none()
    
    if not sesion_obj: return "La sesión no existe."

    # B. REGLA 1: ANTI-BUCLE (Ya está completa?)
    stmt_count = select(func.count(Horario.id)).where(Horario.id_sesion == id_sesion,Horario.estado == 1)
    bloques_asignados = (await db.execute(stmt_count)).scalar() or 0
    
    if bloques_asignados >= sesion_obj.duracion_horas:
        return f"La sesión ya está completa ({bloques_asignados}/{sesion_obj.duracion_horas} horas). No puedes agregar más."

    # C. REGLA 2: CRUCES (Choques)
    id_grupo = sesion_obj.id_grupo
    id_docente = sesion_obj.grupo.id_docente

    conditions = [
        Horario.id_periodo == id_periodo,
        Horario.id_bloque == id_bloque,
        Horario.estado == 1
    ]
    
    conflict_or = [Sesion.id_grupo == id_grupo] # El grupo ya tiene clase
    if id_docente:
        conflict_or.append(and_(Grupo.id_docente == id_docente, Grupo.id_docente.isnot(None)))
    if id_aula:
        conflict_or.append(Horario.id_aula == id_aula)

    stmt_cruce = (
        select(Horario)
        .join(Sesion).join(Grupo)
        .where(and_(*conditions, or_(*conflict_or)))
        .options(joinedload(Horario.sesion).joinedload(Sesion.grupo).joinedload(Grupo.docente))
    )
    cruce = (await db.execute(stmt_cruce)).scalar_one_or_none()

    if cruce:
        detalles = []
        if cruce.sesion.id_grupo == id_grupo: detalles.append(f"El Grupo ya tiene clase ({cruce.sesion.tipo_sesion})")
        if id_docente and cruce.sesion.grupo.id_docente == id_docente: detalles.append(f"El Docente {cruce.sesion.grupo.docente.apellido} ya tiene clase")
        return "CRUCE: " + " | ".join(detalles)

    # D. REGLA 3: RESTRICCIONES (Días bloqueados)
    if id_docente:
        bloque_obj = await db.get(BloqueHorario, id_bloque)
        stmt_rest = select(Restriccion).where(
            Restriccion.entidad_referencia == 'DOCENTE',
            Restriccion.id_entidad == id_docente,
            Restriccion.tipo == 'BLOQUEO_DIA',
            Restriccion.estado == 1
        )
        restricciones = (await db.execute(stmt_rest)).scalars().all()
        for r in restricciones:
            if r.regla_json.get('dia') == bloque_obj.dia_semana:
                return f"El docente tiene restricción el {bloque_obj.dia_semana}."

    return None

# =====================================================================
#  2. ENDPOINTS DE DATOS (GET) - LO QUE TE FALTABA
# =====================================================================

@router.get("/sesiones/pendientes/{id_periodo}", response_model=List[SesionFullResponse]) # <--- CAMBIO AQUÍ
async def get_sesiones_pendientes(id_periodo: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene todas las sesiones del periodo para mostrarlas en el Sidebar.
    """
    return await crud_sesion.get_pendientes_export(db, id_periodo)

@router.get("/bloques/turno/{id_turno}", response_model=List[BloqueHorarioResponse])
async def read_bloques(id_turno: int, db: AsyncSession = Depends(get_db)):
    """Trae los bloques (horas) de un turno específico."""
    return await crud_bloque.get_by_turno(db, id_turno=id_turno)

@router.get("/periodo/{id_periodo}", response_model=List[HorarioResponse])
async def get_horario_periodo(id_periodo: int, db: AsyncSession = Depends(get_db)):
    """Trae todo el horario ya asignado (Fichas en la grilla)."""
    stmt = (
        select(Horario)
        .where(Horario.id_periodo == id_periodo, Horario.estado == 1)
        .options(
            joinedload(Horario.sesion).joinedload(Sesion.grupo).joinedload(Grupo.curso_aperturado).joinedload(import_module('app.models.curso_aperturado').CursoAperturado.curso),
            joinedload(Horario.sesion).joinedload(Sesion.grupo).joinedload(Grupo.docente),
            joinedload(Horario.bloque_horario),
            joinedload(Horario.aula)
        )
    )
    return (await db.execute(stmt)).scalars().all()

@router.get("/periodo/{id_periodo}/ciclos")
async def get_ciclos_en_periodo(id_periodo: int, db: AsyncSession = Depends(get_db)):
    """
    Retorna [1, 3, 5...] o [2, 4, 6...] según la paridad del periodo.
    """
    periodo = await db.get(PeriodoAcademico, id_periodo)
    if not periodo: return []
    
    codigo = str(periodo.codigo).upper().strip()
    es_par = codigo.endswith('II') or codigo.endswith('2') or 'PAR' in codigo
    ciclos = [2, 4, 6, 8, 10] if es_par else [1, 3, 5, 7, 9]
    
    return [{"id": c, "nombre": f"Ciclo {c}"} for c in ciclos]

# =====================================================================
#  3. ENDPOINTS DE ACCIÓN (POST/DELETE)
# =====================================================================

@router.post("/guardar-asignacion", response_model=List[HorarioResponse])
async def asignar_horario_manual(
    payload: HorarioCreate, 
    db: AsyncSession = Depends(get_db)
):
    """
    Asigna una sesión ocupando TODOS los bloques necesarios según su duración.
    """
    # 1. Obtener datos de la sesión
    sesion = await db.get(Sesion, payload.id_sesion)
    if not sesion:
        raise HTTPException(404, "Sesión no encontrada")
    duracion = sesion.duracion_horas

    # 2. Obtener bloque inicio
    bloque_inicio = await db.get(BloqueHorario, payload.id_bloque)
    if not bloque_inicio:
        raise HTTPException(404, "Bloque de inicio no encontrado")

    # 3. Buscar bloques consecutivos
    stmt_bloques = (
        select(BloqueHorario)
        .where(
            BloqueHorario.id_turno == bloque_inicio.id_turno,
            BloqueHorario.dia_semana == bloque_inicio.dia_semana,
            BloqueHorario.orden >= bloque_inicio.orden
        )
        .order_by(BloqueHorario.orden)
        .limit(duracion)
    )
    bloques_a_ocupar = (await db.execute(stmt_bloques)).scalars().all()

    # 4. Validación de espacio
    if len(bloques_a_ocupar) < duracion:
        raise HTTPException(400, f"No hay espacio suficiente. Faltan bloques.")

    # 5. Iterar y Crear
    nuevos_horarios = []
    
    for bloque in bloques_a_ocupar:
        # ... validaciones ...
        nuevo = Horario(
            id_sesion=payload.id_sesion,
            id_bloque=bloque.id,
            id_aula=payload.id_aula,
            id_periodo=payload.id_periodo,
            estado=1
        )
        nuevos_horarios.append(nuevo)

    # 6. Guardar y Recargar
    db.add_all(nuevos_horarios)
    await db.commit()

    # --- CORRECCIÓN AQUÍ ---
    # Refrescamos explícitamente para recuperar los IDs sin error de Greenlet
    for h in nuevos_horarios:
        await db.refresh(h)
    # -----------------------
    
    # Ahora sí podemos leer h.id sin problemas
    ids_nuevos = [h.id for h in nuevos_horarios]
    
    # Traemos los datos completos con sus relaciones (Eager Loading)
    # Importante: Asegúrate que CursoAperturado esté importado
    from app.models.curso_aperturado import CursoAperturado 

    stmt_full = (
        select(Horario)
        .where(Horario.id.in_(ids_nuevos))
        .options(
            joinedload(Horario.sesion).joinedload(Sesion.grupo).joinedload(Grupo.curso_aperturado).joinedload(CursoAperturado.curso),
            joinedload(Horario.sesion).joinedload(Sesion.grupo).joinedload(Grupo.docente),
            joinedload(Horario.bloque_horario),
            joinedload(Horario.aula)
        )
    )
    
    resultados_completos = (await db.execute(stmt_full)).scalars().all()
    return resultados_completos



@router.delete("/{id_horario}")
async def eliminar_horario(id_horario: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina la asignación de horario.
    MEJORA: Busca la sesión asociada y elimina TODOS los bloques de esa sesión
    en el mismo periodo (para que no queden horas sueltas).
    """
    # 1. Buscar el horario específico que se quiere borrar
    horario_a_borrar = await db.get(Horario, id_horario)
    
    if not horario_a_borrar:
        # Si no existe, devolvemos 404 pero no pasa nada grave
        raise HTTPException(status_code=404, detail="Asignación no encontrada (tal vez ya se borró)")

    # 2. Identificar la sesión y el periodo
    id_sesion = horario_a_borrar.id_sesion
    id_periodo = horario_a_borrar.id_periodo

    # 3. Borrar TODOS los registros de esa sesión en este periodo
    # Así limpiamos las 2 o 3 horas completas de la clase
    stmt_delete = (
        delete(Horario)
        .where(
            Horario.id_sesion == id_sesion,
            Horario.id_periodo == id_periodo
        )
    )
    
    await db.execute(stmt_delete)
    await db.commit()
    
    return {"message": "Sesión liberada completamente del horario"}


@router.get("/exportar-excel/grupo/{id_grupo}")
async def exportar_horario_excel(id_grupo: int, db: AsyncSession = Depends(get_db)):
    # ... (Mantén aquí el código de Excel que tenías en gestion_horarios.py)
    #
    pass 

# Nota: He resumido las funciones de exportación para no hacer el código gigante, 
# pero debes copiar el cuerpo de 'exportar_horario_excel' y 'exportar_plantilla_horarios' 
# de tu archivo gestion_horarios.py aquí mismo.


# ==========================================
# 2. ENDPOINTS DE GESTIÓN (Bloques y Sesiones)
# ==========================================

@router.get("/bloques/turno/{id_turno}", response_model = List[BloqueHorarioResponse])
async def read_bloques(id_turno: int, db: AsyncSession = Depends(get_db)):
    return await crud_bloque.get_by_turno(db, id_turno=id_turno)

@router.post("/bloques/masivo")
async def create_bloques_masivos(payload: BloqueMasivoCreate, db: AsyncSession = Depends(get_db)):
    return await crud_bloque.create_bulk(db, payload.id_turno, payload.dias, payload.intervalos)

@router.delete("/bloques/turno/{id_turno}")
async def clear_blocks_by_turno(id_turno: int, db: AsyncSession = Depends(get_db)):
    await crud_bloque.remove_by_turno(db, id_turno=id_turno)
    return {"detail": "Rejilla limpiada"}

@router.get("/sesiones/grupo/{id_grupo}", response_model=List[SesionResponse])
async def get_sesiones_by_grupo(id_grupo: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Sesion).where(Sesion.id_grupo == id_grupo)
    return (await db.execute(stmt)).scalars().all()

@router.post("/sesiones/generar-automatico/{id_grupo}")
async def auto_generar_sesiones(id_grupo: int, db: AsyncSession = Depends(get_db)):
    return await crud_sesion.generar_sesiones_por_grupo(db, id_grupo=id_grupo)
