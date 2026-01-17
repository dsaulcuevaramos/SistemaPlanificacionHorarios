from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, distinct, func, update, and_, delete, cast, Integer
from sqlalchemy.orm import joinedload, aliased

from app.core.database import get_db
# Modelos
from app.models.grupo import Grupo
from app.models.curso_aperturado import CursoAperturado
from app.models.curso import Curso
from app.models.docente import Docente
from app.models.bloque_horario import BloqueHorario
from app.models.horario import Horario
from app.models.sesion import Sesion
from app.models.contrato_docente import ContratoDocente
from app.models.disponibilidad_docente import DisponibilidadDocente

from app.schemas.grupo import GrupoCreateMasivo, GrupoUpdate


from app.models.sesion import Sesion

router = APIRouter()

# =====================================================================
#  FUNCIONES AUXILIARES (Lógica de Negocio)
# =====================================================================

async def actualizar_disponibilidad_docente(db: AsyncSession, id_docente: int, id_periodo: int):
    """
    Suma las horas de los grupos del docente y actualiza la tabla DisponibilidadDocente.
    """
    if not id_docente:
        return

    try:
        # 1. Sumar horas (Casteamos a Integer para evitar problemas de tipos Decimal)
        # Suma = (Horas Teoria + Horas Practica) de todos los grupos de ese periodo
        stmt_sum = (
            select(func.sum(Curso.horas_teoricas + Curso.horas_practicas))
            .join(CursoAperturado, Curso.id == CursoAperturado.id_curso)
            .join(Grupo, CursoAperturado.id == Grupo.id_curso_aperturado)
            .where(
                Grupo.id_docente == id_docente,
                CursoAperturado.id_periodo == id_periodo
            )
        )
        resultado = await db.execute(stmt_sum)
        total_horas = resultado.scalar() or 0
        total_horas = int(total_horas) # Aseguramos que sea int

        # 2. Actualizar DisponibilidadDocente
        # Usamos UPDATE directo que es más rápido y seguro
        stmt_update = (
            update(DisponibilidadDocente)
            .where(
                DisponibilidadDocente.id_docente == id_docente,
                DisponibilidadDocente.id_periodo == id_periodo
            )
            .values(horas_asignadas_actuales=total_horas)
            .execution_options(synchronize_session=False) # Importante para actualizaciones masivas
        )
        await db.execute(stmt_update)
        
        print(f"--- HORAS ACTUALIZADAS: Docente {id_docente} ahora tiene {total_horas} horas ---")

    except Exception as e:
        # Esto imprimirá el error real en tu terminal negra si vuelve a fallar
        print(f"ERROR CRÍTICO ACTUALIZANDO DISPONIBILIDAD: {e}")
        # No lanzamos raise para no tumbar la transacción principal si esto falla, 
        # pero idealmente deberíamos corregirlo.


async def validar_tope_horario(db: AsyncSession, id_docente: int, id_periodo: int, horas_a_sumar: int):
    """
    Consulta el CONTRATO del docente para ver su 'horas_tope_semanales'.
    Si (Horas Actuales + Nuevas) > Tope, lanza error.
    """
    if not id_docente:
        return

    # 1. Obtener Horas ACTUALES (De la disponibilidad)
    stmt_disp = select(DisponibilidadDocente).where(
        DisponibilidadDocente.id_docente == id_docente,
        DisponibilidadDocente.id_periodo == id_periodo
    )
    disp = (await db.execute(stmt_disp)).scalars().first()
    
    if not disp:
        # Si no tiene disponibilidad creada, asumimos 0 horas actuales
        # (Aunque esto debería existir si hay contrato)
        horas_actuales = 0
    else:
        horas_actuales = disp.horas_asignadas_actuales

    # 2. Obtener Tope del CONTRATO (Tu petición: Usar ContratoDocente)
    # Buscamos el contrato activo. Asumimos que validas que solo haya uno por docente/fecha.
    stmt_contrato = select(ContratoDocente).where(
        ContratoDocente.id_docente == id_docente
    )
    contrato = (await db.execute(stmt_contrato)).scalars().first()

    if not contrato:
        # Si no tiene contrato, ¡No debería poder tener grupos!
        raise HTTPException(400, "El docente seleccionado NO TIENE CONTRATO vigente.")
    
    tope_maximo = contrato.horas_tope_semanales

    # 3. Comparar
    nueva_carga = horas_actuales + horas_a_sumar
    
    if nueva_carga > tope_maximo:
        raise HTTPException(
            status_code=400, 
            detail=f"Límite excedido: El docente tiene {horas_actuales} hrs asignadas. Con estas +{horas_a_sumar} llegaría a {nueva_carga}, superando su contrato de {tope_maximo} hrs."
        )


# =====================================================================
#  ENDPOINTS
# =====================================================================

# ... (Tus endpoints GET de get_ciclos_en_periodo, get_grupos_by_ciclo, get_cursos_con_grupos MANTENLOS IGUAL) ...
# Pego aquí solo los que cambian lógica de negocio:

@router.get("/periodo/{id_periodo}/ciclos")
async def get_ciclos_en_periodo(id_periodo: int, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(distinct(Curso.ciclo))
        .join(CursoAperturado, Curso.id == CursoAperturado.id_curso)
        .join(Grupo, CursoAperturado.id == Grupo.id_curso_aperturado)
        .where(CursoAperturado.id_periodo == id_periodo)
        .order_by(Curso.ciclo)
    )
    result = await db.execute(stmt)
    ciclos_raw = result.scalars().all()
    response = []
    for c in ciclos_raw:
        response.append({"id": c, "nombre": f"Ciclo {c}"})
    return response

@router.get("/ciclo/{ciclo}")
async def get_grupos_by_ciclo(ciclo: int, id_periodo: int = None, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Grupo)
        .join(CursoAperturado, Grupo.id_curso_aperturado == CursoAperturado.id)
        .join(Curso, CursoAperturado.id_curso == Curso.id)
        .where(Curso.ciclo == ciclo)
    )
    if id_periodo:
        stmt = stmt.where(CursoAperturado.id_periodo == id_periodo)
    
    stmt = stmt.options(
        joinedload(Grupo.turno),
        joinedload(Grupo.curso_aperturado).joinedload(CursoAperturado.curso)
    )
    result = await db.execute(stmt)
    grupos = result.scalars().all()
    for g in grupos:
        # Esto permite que el front haga: if (grupo.ciclo === cicloSeleccionado)
        setattr(g, "ciclo", g.curso_aperturado.curso.ciclo)
        setattr(g, "curso_nombre", g.curso_aperturado.curso.nombre)
        if g.docente:
            setattr(g, "docente_nombre", f"{g.docente.apellido}")
    
    return grupos

@router.get("/periodo/{id_periodo}/detallado")
async def get_cursos_con_grupos(id_periodo: int, db: AsyncSession = Depends(get_db)):
    try:
        stmt = (
            select(CursoAperturado)
            .where(CursoAperturado.id_periodo == id_periodo)
            .options(
                joinedload(CursoAperturado.curso),
                joinedload(CursoAperturado.grupos).joinedload(Grupo.docente),
                joinedload(CursoAperturado.grupos).joinedload(Grupo.turno)
            )
            .order_by(CursoAperturado.id)
        )
        result = await db.execute(stmt)
        return result.unique().scalars().all()
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno al cargar grupos: {str(e)}")


@router.post("/generar-lote")
async def crear_grupos_masivo(payload: GrupoCreateMasivo, db: AsyncSession = Depends(get_db)):
    print(f"--- INICIO GENERAR LOTE ---")
    
    try:
        # 1. Obtener datos del curso (y guardar variables simples ANTES de cualquier operación)
        stmt_curso = (
            select(CursoAperturado)
            .options(joinedload(CursoAperturado.curso))
            .where(CursoAperturado.id == payload.id_curso_aperturado)
        )
        curso_ap = (await db.execute(stmt_curso)).scalars().first()
        if not curso_ap: raise HTTPException(404, "Curso aperturado no existe")

        # Guardamos datos clave en variables simples (Int/Str) para no depender del objeto DB
        target_periodo_id = curso_ap.id_periodo
        target_ciclo = curso_ap.curso.ciclo
        h_teoria = int(curso_ap.curso.horas_teoricas or 0)
        h_practica = int(curso_ap.curso.horas_practicas or 0)
        horas_totales_curso = h_teoria + h_practica
        total_horas_nuevas = horas_totales_curso * payload.cantidad_grupos 

        # 2. VALIDAR TOPE (Luz Roja)
        if payload.id_docente:
            await validar_tope_horario(db, payload.id_docente, target_periodo_id, total_horas_nuevas)

        # 3. PREPARAR OBJETOS (GRUPOS + SESIONES) EN MEMORIA
        letras = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        stmt_count = select(func.count()).select_from(Grupo).where(Grupo.id_curso_aperturado == payload.id_curso_aperturado)
        existentes = (await db.execute(stmt_count)).scalar() or 0
        
        nuevos_grupos = []
        
        for i in range(payload.cantidad_grupos):
            # A) Crear Grupo
            indice_real = existentes + i
            nombre_grupo = letras[indice_real] if indice_real < len(letras) else f"Grupo {indice_real + 1}"
            
            nuevo_grupo = Grupo(
                nombre=nombre_grupo,
                id_curso_aperturado=payload.id_curso_aperturado,
                id_docente=payload.id_docente,
                id_turno=payload.id_turno,
                vacantes=payload.vacantes_por_grupo
            )
            
            # B) Crear Sesiones Automáticas (VINCULADAS DIRECTAMENTE AL OBJETO GRUPO)
            # Truco: Al pasar `grupo=nuevo_grupo`, SQLAlchemy entiende la relación sin necesitar el ID aún.
            
            # Sesión Teórica
            if h_teoria > 0:
                sesion_t = Sesion(
                    tipo_sesion='TEORIA',
                    duracion_horas=h_teoria,
                    grupo=nuevo_grupo, # Vinculación en memoria
                    estado=1
                )
                db.add(sesion_t) # Agregamos a la sesión
            
            # Sesión Práctica
            if h_practica > 0:
                sesion_p = Sesion(
                    tipo_sesion='PRACTICA',
                    duracion_horas=h_practica,
                    grupo=nuevo_grupo, # Vinculación en memoria
                    estado=1
                )
                db.add(sesion_p)

            nuevos_grupos.append(nuevo_grupo)
            await crear_esqueleto_horario(db, nuevo_grupo, target_periodo_id, target_ciclo)
        
        # 4. GUARDAR TODO (FLUSH)
        db.add_all(nuevos_grupos)
        
        # FLUSH: Envía a la BD, genera IDs, pero NO cierra la transacción.
        # Esto permite que 'actualizar_disponibilidad' vea los datos nuevos sin romper la sesión async.
        await db.flush() 

        # 5. ACTUALIZAR DISPONIBILIDAD (Luz Verde)
        if payload.id_docente:
            print(f"Actualizando horas para docente {payload.id_docente}...")
            # Como usamos flush(), esta función ya puede "ver" los grupos nuevos en la BD
            await actualizar_disponibilidad_docente(db, payload.id_docente, target_periodo_id)

        # 6. COMMIT FINAL (Ahora sí cerramos todo)
        await db.commit()

        return {"message": f"Se crearon {len(nuevos_grupos)} grupos y sus sesiones correspondientes."}

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"ERROR CRÍTICO: {e}")
        # Rollback importante por si falla a medias
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.put("/{id_grupo}")
async def actualizar_grupo(id_grupo: int, payload: GrupoUpdate, db: AsyncSession = Depends(get_db)):
    # 1. Obtener grupo
    stmt = (
        select(Grupo)
        .options(joinedload(Grupo.curso_aperturado).joinedload(CursoAperturado.curso))
        .where(Grupo.id == id_grupo)
    )
    result = await db.execute(stmt)
    grupo = result.scalars().first()
    
    if not grupo: raise HTTPException(404, "Grupo no encontrado")

    curso = grupo.curso_aperturado.curso
    id_periodo = grupo.curso_aperturado.id_periodo
    horas_curso = curso.horas_teoricas + curso.horas_practicas
    
    docente_anterior = grupo.id_docente
    nuevo_docente = payload.id_docente

    # 2. Si cambia el docente
    if nuevo_docente != docente_anterior:
        
        # Validar al nuevo
        if nuevo_docente is not None:
            await validar_tope_horario(db, nuevo_docente, id_periodo, horas_curso)
        
        # Aplicar cambio
        grupo.id_docente = nuevo_docente
        if payload.id_turno is not None: grupo.id_turno = payload.id_turno
        if payload.vacantes is not None: grupo.vacantes = payload.vacantes
        
        await db.commit() # Guardar cambio de dueño
        
        # Actualizar horas de ambos
        if nuevo_docente:
            await actualizar_disponibilidad_docente(db, nuevo_docente, id_periodo)
        if docente_anterior:
            await actualizar_disponibilidad_docente(db, docente_anterior, id_periodo)
            
        await db.commit() 

    else:
        # Actualización simple
        if payload.id_turno is not None: grupo.id_turno = payload.id_turno
        if payload.vacantes is not None: grupo.vacantes = payload.vacantes
        await db.commit()
    
    await db.refresh(grupo)
    return {"message": "Grupo actualizado", "grupo": grupo}


@router.delete("/{id_grupo}")
async def eliminar_grupo(id_grupo: int, db: AsyncSession = Depends(get_db)):
    # 1. Obtener el grupo
    stmt = select(Grupo).options(joinedload(Grupo.curso_aperturado)).where(Grupo.id == id_grupo)
    grupo = (await db.execute(stmt)).scalars().first()
    
    if not grupo: raise HTTPException(404, "Grupo no encontrado")
    
    id_docente_afectado = grupo.id_docente
    id_periodo = grupo.curso_aperturado.id_periodo

    # 2. OBTENER IDs DE LAS SESIONES DEL GRUPO
    stmt_ids = select(Sesion.id).where(Sesion.id_grupo == id_grupo)
    ids_sesiones = (await db.execute(stmt_ids)).scalars().all()

    # 3. LIMPIEZA PROFUNDA (ESTO ES LO QUE FALTABA)
    if ids_sesiones:
        # A. Borrar referencias en HORARIO (El candado que te daba error 500)
        stmt_del_horario = delete(Horario).where(Horario.id_sesion.in_(ids_sesiones))
        await db.execute(stmt_del_horario)

        # B. Ahora sí, borrar las SESIONES
        stmt_del_sesiones = delete(Sesion).where(Sesion.id == Sesion.id).where(Sesion.id_grupo == id_grupo)
        await db.execute(stmt_del_sesiones)

    # 4. Finalmente, borrar el GRUPO
    await db.delete(grupo)
    
    # 5. Actualizar disponibilidad del docente si es necesario
    if id_docente_afectado:
        await db.commit() # Commit parcial
        await actualizar_disponibilidad_docente(db, id_docente_afectado, id_periodo)
    
    await db.commit()
    return {"message": "Grupo eliminado y horario limpiado correctamente"}


async def crear_esqueleto_horario(db: AsyncSession, grupo_obj: Grupo, id_periodo: int, ciclo: int):
    """
    Crea las filas vacías (id_sesion=NULL) en la tabla Horario para un grupo nuevo.
    """
    # 1. Traer todos los bloques del turno de ese grupo
    stmt = select(BloqueHorario).where(
        BloqueHorario.id_turno == grupo_obj.id_turno,
        BloqueHorario.estado == 1
    )
    bloques = (await db.execute(stmt)).scalars().all()
    
    casillas = []
    for b in bloques:
        casilla = Horario(
            id_sesion=None,     # VACÍO POR DEFECTO
            id_bloque=b.id,
            id_periodo=id_periodo,
            id_aula=None,
            ciclo=ciclo,        # Dato redundante útil
            grupo=grupo_obj.nombre, # Dato redundante útil
            estado=1
        )
        casillas.append(casilla)
    
    if casillas:
        db.add_all(casillas)

"""
# En routers/grupos.py (Arriba, junto a las otras funciones auxiliares)
from app.models.sesion import Sesion # Asegúrate de importar esto

async def generar_sesiones_automaticas(db: AsyncSession, grupos_creados: list, h_teoria: int, h_practica: int):
  
    #Crea las sesiones automáticamente basadas en las horas simples (int).
    
    sesiones_nuevas = []
    
    for grupo in grupos_creados:
        # 1. Sesión de TEORÍA
        if h_teoria > 0:
            s_teoria = Sesion(
                tipo_sesion='TEORIA',
                duracion_horas=h_teoria,
                id_grupo=grupo.id, # El ID ya existe porque hicimos commit previo
                estado=1
            )
            sesiones_nuevas.append(s_teoria)
            
        # 2. Sesión de PRÁCTICA
        if h_practica > 0:
            s_practica = Sesion(
                tipo_sesion='PRACTICA',
                duracion_horas=h_practica,
                id_grupo=grupo.id,
                estado=1
            )
            sesiones_nuevas.append(s_practica)
    
    if sesiones_nuevas:
        db.add_all(sesiones_nuevas)
        await db.commit() # Guardamos las sesiones
        print(f"--- AUTO-GENERACIÓN: Se crearon {len(sesiones_nuevas)} sesiones ---")

"""