"""# app/api/v1/endpoints/malla.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps # get_db, get_current_user
from app.services.malla_service import malla_service
from app.models.usuario import Usuario 
from typing import Dict, List, Any

router = APIRouter(prefix="/malla", tags=["Malla Curricular / Grafos"])

@router.get(
    "/{id_plan_version}", 
    response_model=Dict[str, List[Dict[str, Any]]],
    summary="Obtener la Malla Curricular como un Grafo (Nodos y Aristas)"
)
async def get_malla_view_data(
    id_plan_version: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: Usuario = Depends(deps.get_current_user) 
):
    """"""
    Devuelve la estructura de datos (Nodos y Edges) necesaria para pintar 
    la Malla Curricular Gráfica usando Vue Flow para una versión de Plan específica.
    Asegura que el plan pertenezca a la escuela del usuario logueado.
    """"""
    
    # NOTA DE SEGURIDAD: La validación de que el plan_version pertenece a id_escuela 
    # se realiza DENTRO del servicio (get_malla_data) mediante JOINs.
    
    try:
        data = await malla_service.get_malla_data(
            db=db, 
            id_plan_version=id_plan_version, 
            id_escuela=current_user.id_escuela
        )
        
        if not data["nodes"]:
            # Esto puede significar que el plan no existe o no tiene cursos.
            # Podrías añadir una validación más estricta si el plan_version no existe.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Malla no encontrada o Plan de Estudios vacío para esta versión."
            )
            
        return data
        
    except Exception as e:
        # En caso de un error de consulta inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al generar el grafo: {str(e)}"
        )"""