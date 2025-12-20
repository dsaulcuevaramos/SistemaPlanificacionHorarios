from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario

# Importamos los modelos para la base de datos
from app.models.contrato_docente import ContratoDocente
from app.models.disponibilidad_docente import DisponibilidadDocente
from app.models.periodo_academico import PeriodoAcademico

# Importamos los esquemas para validación de respuesta
from app.schemas.disponibilidad_docente import DisponibilidadDocenteResponse
# Importamos la instancia del CRUD
from app.crud.crud_contrato_docente import contrato_docente

router = APIRouter()

@router.get("/disponibilidad/periodo/{id_periodo}", response_model=List[DisponibilidadDocenteResponse])
async def read_disponibilidad_periodo(
    id_periodo: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Obtiene la lista de docentes ya asignados a un periodo."""
    # Nota: Asegúrate que tu crud_disponibilidad tenga el método get_by_periodo
    from app.crud.crud_disponibilidad_docente import disponibilidad_docente as crud_disp
    return await crud_disp.get_by_periodo(db, id_periodo=id_periodo)

@router.post("/asignar-periodo")
async def crear_contrato_automatico(
    payload: dict, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea el ContratoDocente (usando fechas del periodo) y la DisponibilidadDocente.
    """
    # 1. Validamos el Periodo para obtener las fechas oficiales
    stmt_period = select(PeriodoAcademico).where(PeriodoAcademico.id == payload.get('id_periodo'))
    result = await db.execute(stmt_period)
    periodo = result.scalars().first()

    if not periodo:
        raise HTTPException(status_code=404, detail="El periodo académico no existe.")

    try:
        # 2. Creamos la instancia del ContratoDocente (Usando el Modelo de SQLAlchemy)
        # Ignoramos las fechas que vengan del front; usamos las del periodo.
        nuevo_contrato = ContratoDocente(
            id_docente=payload['id_docente'],
            fecha_inicio=periodo.fecha_inicio, 
            fecha_fin=periodo.fecha_fin,
            horas_tope_semanales=payload.get('horas_tope_semanales', 20),
            turnos_preferidos=payload.get('turnos_preferidos', 'MAÑANA')
        )
        
        # 3. Creamos la DisponibilidadDocente
        nueva_disponibilidad = DisponibilidadDocente(
            id_docente=payload['id_docente'],
            id_periodo=periodo.id,
            horas_asignadas_actuales=0
        )

        # 4. Agregamos ambos objetos a la sesión
        db.add(nuevo_contrato)
        db.add(nueva_disponibilidad)
        
        # Guardamos la transacción
        await db.commit()
        
        return {"msg": "Docente contratado y asignado exitosamente con fechas del periodo."}
        
    except KeyError as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Falta el campo obligatorio: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail=f"Error en la base de datos: {str(e)}")

@router.delete("/quitar-contrato/{id_periodo}/{id_docente}")
async def delete_contrato(
    id_periodo: int, 
    id_docente: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina tanto el contrato como la disponibilidad del docente."""
    success = await contrato_docente.eliminar_contrato_completo(db, id_docente=id_docente, id_periodo=id_periodo)
    if not success:
         raise HTTPException(status_code=404, detail="No se encontró el contrato para eliminar.")
    return {"msg": "Contrato y disponibilidad eliminados."}