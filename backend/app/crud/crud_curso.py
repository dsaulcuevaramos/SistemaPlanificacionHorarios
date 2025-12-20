from app.crud.base import CRUDBase
from app.models.curso import Curso
from app.models.plan_version import PlanVersion 
from app.models.plan_estudio import PlanEstudio
from app.schemas.curso import CursoCreate, CursoUpdate

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Union, Any
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

from fastapi.encoders import jsonable_encoder
from sqlalchemy import join


class CRUDCurso(CRUDBase[Curso, CursoCreate, CursoUpdate]):
    pass

    async def get_multi_by_escuela(
        self, db: AsyncSession, *, id_escuela: Optional[int], skip: int = 0, limit: int = 100
    ) -> List[Curso]:
        """
        Obtiene cursos filtrados por escuela, cargando PlanVersion y REQUISITOS.
        """
        
        stmt = (
            select(self.model)
            .join(Curso.plan_version)
            .join(PlanVersion.plan_estudio)
            .options(
                # 1. Cargamos la versión del plan (que ya tenías seguramente)
                selectinload(Curso.plan_version),
                
                # 2. CRÍTICO: Cargar la relación de requisitos para evitar MissingGreenlet
                selectinload(Curso.requisitos) 
            )
            .offset(skip)
            .limit(limit)
        )
        
        if id_escuela is not None:
            stmt = stmt.where(PlanEstudio.id_escuela == id_escuela)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CursoCreate) -> Curso:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        
        # 1. COMMIT
        await db.commit()
        
        # 2. NO leas db_obj.id aquí si no es necesario, pero si db_obj 
        #    ya tenía ID (autoincrement), mejor usa db.refresh explícito 
        #    O BIEN, usa el truco del ID guardado si lo generas tú.
        #    Para autoincrement, lo correcto es:
        await db.refresh(db_obj) # Esto refresca el objeto de forma ASÍNCRONA segura
        
        # 3. Ahora cargamos relaciones
        return await self.get_with_relations(db, id=db_obj.id)

    # --- CORRECCIÓN CRÍTICA EN UPDATE ---
    async def update(
        self, db: AsyncSession, *, db_obj: Curso, obj_in: Union[CursoUpdate, Dict[str, Any]]
    ) -> Curso:
        # 1. Guardamos el ID en una variable ANTES de tocar nada
        #    (Aunque el ID no cambie, acceder a db_obj.id después del commit es peligroso)
        curso_id = db_obj.id 
        
        # Lógica de actualización estándar
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        
        # 2. COMMIT (Aquí el objeto 'db_obj' muere/expira)
        await db.commit()
        
        # 3. USAMOS LA VARIABLE 'curso_id', NO 'db_obj.id'
        #    Al pasar un entero simple, SQLAlchemy no intenta refrescar el objeto viejo
        return await self.get_with_relations(db, id=curso_id)

    # TAMBIÉN ACTUALIZA EL GET INDIVIDUAL SI LO USAS
    async def get_with_relations(self, db: AsyncSession, id: int) -> Optional[Curso]:
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.plan_version),
                selectinload(self.model.requisitos) # <--- AQUÍ TAMBIÉN
            )
            .where(self.model.id == id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()
    
    
curso = CRUDCurso(Curso)