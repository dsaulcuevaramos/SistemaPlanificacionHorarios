# app/services/malla_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.curso import Curso
from app.models.requisito_curso import RequisitoCurso
from app.schemas.curso import CursoReadSimple
from typing import List, Dict, Any

class MallaGrafoService:
    """
    Servicio encargado de consultar la malla curricular y transformarla
    en una estructura de nodos y aristas para la visualización gráfica (Vue Flow).
    """ 

    async def get_malla_data(
        self, 
        db: AsyncSession, 
        id_plan_version: int,
        id_escuela: int # Para asegurar la multi-tenancy a nivel de servicio
    ) -> Dict[str, List[Dict[str, Any]]]:
        
        # 1. Obtener todos los Cursos para la versión de plan y la escuela (JOIN complejo)
        # NOTA: Esto asume que tienes las relaciones correctas en PlanVersion -> PlanEstudio.
        from app.models.plan_version import PlanVersion
        from app.models.plan_estudio import PlanEstudio

        # Consulta que trae todos los cursos activos del plan_version y filtra por escuela
        stmt_cursos = (
            select(Curso)
            .join(PlanVersion)
            .join(PlanEstudio)
            .where(Curso.id_plan_version == id_plan_version)
            .where(PlanEstudio.id_escuela == id_escuela)
            .where(Curso.estado == 1)
            .order_by(Curso.ciclo, Curso.codigo)
        )
        cursos_data = (await db.execute(stmt_cursos)).scalars().all()
        
        if not cursos_data:
            return {"nodes": [], "edges": []}

        # Extraer los IDs de los cursos para el filtro de requisitos
        curso_ids = [c.id for c in cursos_data]

        # 2. Obtener todas las relaciones de prerrequisitos (Edges)
        stmt_requisitos = select(RequisitoCurso).where(
            # Solo relaciones donde el requisito O el dependiente están en nuestra lista de cursos
            RequisitoCurso.id_curso_requisito.in_(curso_ids),
            RequisitoCurso.id_curso_dependiente.in_(curso_ids),
            RequisitoCurso.estado == 1
        )
        requisitos_data = (await db.execute(stmt_requisitos)).scalars().all()

        # 3. Transformación a formato Vue Flow (Nodes y Edges)
        
        nodes = []
        # Mapa para asignar posiciones X (dentro del ciclo) y Y (ciclo)
        cycle_counts = {} 

        # Crear Nodos (Cursos)
        for curso in cursos_data:
            ciclo_str = str(curso.ciclo)
            
            # Contar la posición dentro del ciclo para el eje X
            cycle_counts[ciclo_str] = cycle_counts.get(ciclo_str, 0) + 1
            
            nodes.append({
                'id': str(curso.id),
                'type': 'default', # Tipo de nodo para Vue Flow
                'position': {
                    # Eje X: Basado en el conteo dentro del ciclo (offset * índice)
                    'x': (cycle_counts[ciclo_str] - 1) * 300, 
                    # Eje Y: Basado en el número de ciclo (offset * ciclo)
                    'y': (curso.ciclo - 1) * 150
                },
                'data': {
                    'label': f"({curso.codigo}) - {curso.nombre}",
                    'ciclo': curso.ciclo,
                    'creditos': curso.creditos,
                    'tipo': curso.tipo_curso,
                    'paridad': curso.paridad
                }
            })

        edges = []
        # Crear Edges (Prerrequisitos)
        for req in requisitos_data:
            edges.append({
                'id': f"e{req.id_curso_requisito}-{req.id_curso_dependiente}",
                'source': str(req.id_curso_requisito), # El curso que se requiere
                'target': str(req.id_curso_dependiente), # El curso que depende
                'type': 'step', # Estilo de línea (o 'default')
                'animated': False,
                'label': req.tipo_requisito
            })
            
        return {"nodes": nodes, "edges": edges}

malla_service = MallaGrafoService()