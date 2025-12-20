# app/crud/base.py
from typing import TypeVar, Generic, Type, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.base import Base # Asume la Base

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from fastapi.encoders import jsonable_encoder



# Definimos tipos genéricos
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        Objeto CRUD con métodos por defecto para Crear, Leer, Actualizar, Borrar (CRUD).
        **model**: Un modelo de SQLAlchemy (clase)
        """
        self.model = model

    # Método para buscar por ID
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        return result.scalars().first()

    # Método para buscar todo
    async def get_multi(self, db: AsyncSession, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # Método para crear un nuevo registro
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict() #obj_in_data = jsonable_encoder(obj_in)      #obj_in_data = obj_in.model_dump()
        
        db_obj = self.model(**obj_in_data)          # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    # Metodo para actualizar
    async def update(self,db: AsyncSession,*,db_obj: ModelType,obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        
        # Maneja si viene como dict o como Pydantic model
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            # exclude_unset=True es CLAVE: solo actualiza lo que enviaste
            update_data = obj_in.model_dump(exclude_unset=True) 

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

       
    #Metodo Borrado logico
    async def delete(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:

        stmt = select(self.model).where(self.model.id == id)
        result = await db.execute(stmt)
        obj = result.scalars().first()

        if obj:
            setattr(obj, "estado", 0)
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
        return obj

    #Metodo Eliminación Fisica
    async def remove(self, db: AsyncSession, *, id: int) -> Optional[ModelType]:
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj