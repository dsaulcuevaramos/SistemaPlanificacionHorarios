import asyncio
import logging

# Nota: Ajusta si estás en Windows y tienes problemas con asyncio
# import sys
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.database import engine, SessionLocal
from app.models.base import Base

# Importamos SOLO lo que existe
from app.models import Usuario, Escuela, Catalogo 
from app.crud.crud_usuario import usuario as crud_usuario
from app.schemas.usuario import UsuarioCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_db():
    async with engine.begin() as conn:
        # 1. Crear Tablas
        await conn.run_sync(Base.metadata.create_all)
    
    async with SessionLocal() as db:
        # 2. Crear SuperAdmin
        logger.info("Verificando SuperAdmin...")
        admin = await crud_usuario.get_by_username(db, username="admin")
        
        if not admin:
            logger.info("Creando SuperUsuario 'admin'...")
            admin_in = UsuarioCreate(
                username="admin",
                password="admin123",
                email="admin@unu.edu.pe",
                dni="00000000",
                rol="ADMIN",
                id_escuela=None
            )
            await crud_usuario.create(db, obj_in=admin_in)
            logger.info("¡SuperUsuario creado exitosamente!")
        else:
            logger.info("El SuperUsuario ya existe.")

async def main():
    logger.info("Iniciando inicialización de DB")
    await init_db()
    logger.info("Inicialización terminada")

if __name__ == "__main__":
    asyncio.run(main())