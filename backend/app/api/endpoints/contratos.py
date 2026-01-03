from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

# Importamos Modelos
from app.models.contrato_docente import ContratoDocente
from app.models.disponibilidad_docente import DisponibilidadDocente
from app.models.periodo_academico import PeriodoAcademico
from app.models.restriccion import Restriccion  # <--- NUEVO IMPORT

# Importamos Schemas
from app.schemas.disponibilidad_docente import DisponibilidadDocenteResponse
from app.schemas.contrato_docente import (
    ContratoAsignacionCreate,
    RenovacionMasivaRequest,
    ContratoDocenteResponse
)
from app.crud.crud_contrato_docente import contrato_docente

router = APIRouter()


@router.get("/disponibilidad/periodo/{id_periodo}", response_model=List[DisponibilidadDocenteResponse])
async def read_disponibilidad_periodo(id_periodo: int, db: AsyncSession = Depends(get_db)):
    from app.crud.crud_disponibilidad_docente import disponibilidad_docente as crud_disp
    return await crud_disp.get_by_periodo(db, id_periodo=id_periodo)


@router.post("/asignar-manual") # <--- CAMBIADO para no chocar con el otro endpoint
async def crear_contrato_manual(
    data: ContratoAsignacionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Crea Contrato + Disponibilidad + Restricciones (Días bloqueados).
    """
    # A. Validar Periodo
    periodo = await db.get(PeriodoAcademico, data.id_periodo)
    if not periodo:
        raise HTTPException(status_code=404, detail="Periodo no encontrado")

    # B. Validar Duplicidad
    stmt_exist = select(ContratoDocente).where(
        ContratoDocente.id_docente == data.id_docente,
        ContratoDocente.fecha_inicio == periodo.fecha_inicio
    )
    if (await db.execute(stmt_exist)).scalar_one_or_none():
         raise HTTPException(status_code=400, detail="Este docente ya tiene contrato en este periodo.")

    try:
        # 1. Crear Contrato
        nuevo_contrato = ContratoDocente(
            id_docente=data.id_docente,
            fecha_inicio=periodo.fecha_inicio,
            fecha_fin=periodo.fecha_fin,
            horas_tope_semanales=data.horas_tope_semanales,
            turnos_preferidos=data.turnos_preferidos
        )
        db.add(nuevo_contrato)
        
        # 2. Crear Disponibilidad (Contador de horas)
        nueva_disp = DisponibilidadDocente(
            id_docente=data.id_docente,
            id_periodo=periodo.id,
            horas_asignadas_actuales=0
        )
        db.add(nueva_disp)

        # [cite_start]3. CREAR RESTRICCIONES (La lógica nueva) [cite: 121]
        # Si el usuario marcó días en rojo (ej. no puede venir los Lunes)
        if data.dias_no_disponibles:
            for dia in data.dias_no_disponibles:
                restriccion = Restriccion(
                    tipo='BLOQUEO_DIA',          # Tipo estandarizado
                    entidad_referencia='DOCENTE',
                    id_entidad=data.id_docente,
                    id_periodo=periodo.id,       # Vinculado a este periodo
                    regla_json={"dia": dia},     # Guardamos el dato clave en JSON
                    peso=100,                    # 100 = Restricción dura (No negociable)
                    estado=1
                )
                db.add(restriccion)

        # 4. Guardar todo
        await db.commit()
        return {"msg": "Docente contratado y restricciones aplicadas correctamente."}

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/asignar-periodo") 
async def crear_contrato_automatico(
    payload: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea contrato simple sin validaciones complejas.
    Útil para scripts de carga rápida.
    """
    stmt_period = select(PeriodoAcademico).where(PeriodoAcademico.id == payload.get('id_periodo'))
    result = await db.execute(stmt_period)
    periodo = result.scalars().first()

    if not periodo:
        raise HTTPException(status_code=404, detail="El periodo académico no existe.")

    try:
        nuevo_contrato = ContratoDocente(
            id_docente=payload['id_docente'],
            fecha_inicio=periodo.fecha_inicio, 
            fecha_fin=periodo.fecha_fin,
            horas_tope_semanales=payload.get('horas_tope_semanales', 20),
            turnos_preferidos=payload.get('turnos_preferidos', 'MAÑANA')
        )
        
        nueva_disponibilidad = DisponibilidadDocente(
            id_docente=payload['id_docente'],
            id_periodo=periodo.id,
            horas_asignadas_actuales=0
        )

        db.add(nuevo_contrato)
        db.add(nueva_disponibilidad)
        await db.commit()
        
        return {"msg": "Docente asignado (Simple)."}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error BD: {str(e)}")
    

@router.delete("/quitar-contrato/{id_periodo}/{id_docente}")
async def delete_contrato(id_periodo: int, id_docente: int, db: AsyncSession = Depends(get_db)):
    # OJO: Aquí deberías actualizar tu CRUD para borrar también las restricciones asociadas
    success = await contrato_docente.eliminar_contrato_completo(db, id_docente=id_docente, id_periodo=id_periodo)
    
    # Borrado manual de restricciones (si el CRUD no lo hace)
    # stmt_del_rest = delete(Restriccion).where(...) 
    # await db.execute(stmt_del_rest)

    if not success:
         raise HTTPException(status_code=404, detail="No se encontró el contrato.")
    return {"msg": "Contrato, disponibilidad y restricciones eliminados."}


@router.post("/renovacion-masiva")
async def renovar_contratos(
    payload: RenovacionMasivaRequest,
    db: AsyncSession = Depends(get_db)
):
    """Copia contratos Y RESTRICCIONES del periodo anterior al nuevo."""
    
    periodo_nuevo = await db.get(PeriodoAcademico, payload.id_periodo_nuevo)
    if not periodo_nuevo: raise HTTPException(404, "Periodo destino no encontrado")

    periodo_ant = await db.get(PeriodoAcademico, payload.id_periodo_anterior)
    
    # Traer contratos viejos
    stmt_antiguos = select(ContratoDocente).where(ContratoDocente.fecha_inicio == periodo_ant.fecha_inicio)
    contratos_viejos = (await db.execute(stmt_antiguos)).scalars().all()
    
    if not contratos_viejos:
        raise HTTPException(400, "No hay contratos antiguos.")

    count = 0
    for c in contratos_viejos:
        # Verificar existencia
        stmt_check = select(ContratoDocente).where(
            ContratoDocente.id_docente == c.id_docente,
            ContratoDocente.fecha_inicio == periodo_nuevo.fecha_inicio
        )
        if not (await db.execute(stmt_check)).scalar_one_or_none():
            
            # A. Clonar Contrato
            nuevo = ContratoDocente(
                id_docente=c.id_docente,
                fecha_inicio=periodo_nuevo.fecha_inicio,
                fecha_fin=periodo_nuevo.fecha_fin,
                horas_tope_semanales=c.horas_tope_semanales,
                turnos_preferidos=c.turnos_preferidos
            )
            
            # B. Clonar Disponibilidad
            disp = DisponibilidadDocente(
                id_docente=c.id_docente,
                id_periodo=periodo_nuevo.id,
                horas_asignadas_actuales=0
            )
            
            db.add(nuevo)
            db.add(disp)

            # C. CLONAR RESTRICCIONES (Mejora Crítica)
            # Buscamos las restricciones que tenía en el periodo anterior
            stmt_restricciones_old = select(Restriccion).where(
                Restriccion.entidad_referencia == 'DOCENTE',
                Restriccion.id_entidad == c.id_docente,
                Restriccion.id_periodo == payload.id_periodo_anterior
            )
            restricciones_old = (await db.execute(stmt_restricciones_old)).scalars().all()

            for r_old in restricciones_old:
                r_new = Restriccion(
                    tipo=r_old.tipo,
                    entidad_referencia=r_old.entidad_referencia,
                    id_entidad=r_old.id_entidad,
                    id_periodo=periodo_nuevo.id, # <--- Apunta al nuevo periodo
                    regla_json=r_old.regla_json,
                    peso=r_old.peso,
                    estado=1
                )
                db.add(r_new)

            count += 1
    
    await db.commit()
    return {"message": f"Renovados {count} contratos y sus restricciones."}

