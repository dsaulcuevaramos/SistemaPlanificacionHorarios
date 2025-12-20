# app/crud/crud_usuario.py
from typing import Optional, Dict, Any, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate


class CRUDUsuario(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):

    # 1. Búsqueda por Username (Para el Login)
    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    # Nuevo helper para validar DNI (Para tu recuperación de contraseña)
    async def get_by_dni(self, db: AsyncSession, dni: str) -> Optional[Usuario]:
        stmt = select(Usuario).where(Usuario.dni == dni)
        result = await db.execute(stmt)
        return result.scalars().first()

    # 2. Sobrescribir CREATE para hashear password
    async def create(self, db: AsyncSession, *, obj_in: UsuarioCreate) -> Usuario:
        obj_in_data = obj_in.model_dump()                           # Convertimos a dict
        password_plano = obj_in_data.pop("password")                # Sacamos el password plano y lo hasheamos
        hashed_password = get_password_hash(password_plano)    
        db_obj = Usuario(**obj_in_data, password=hashed_password)   # Creamos el objeto con el hash
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    

    # 3. Sobrescribir UPDATE por si cambian el password
    async def update(self, db: AsyncSession, *, db_obj: Usuario, obj_in: Union[UsuarioUpdate, Dict[str, Any]]) -> Usuario:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
            
        # Si envían un nuevo password, lo hasheamos antes de pasar al padre
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["password"] = hashed_password
            
        return await super().update(db, db_obj=db_obj, obj_in=update_data)
    
    # 4. Método auxiliar para autenticar (Login)
    async def authenticate(self, db: AsyncSession, username_or_email: str, password: str) -> Optional[Usuario]:
        # Buscamos si coincide con username O con email
        stmt = select(Usuario).where(
            or_(
                Usuario.username == username_or_email, 
                Usuario.email == username_or_email
            )
        )
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


    async def get_by_username_or_email(self, db: AsyncSession, username_or_email: str) -> Optional[Usuario]:
        """Obtiene un usuario por su nombre de usuario o su correo electrónico."""
        stmt = select(self.model).where(
            or_(
                self.model.username == username_or_email,
                self.model.email == username_or_email
            )
        )
        result = await db.execute(stmt)
        return result.scalars().first()

# Instancia global para ser importada en los routers
usuario = CRUDUsuario(Usuario)
