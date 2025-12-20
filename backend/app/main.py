from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.api import api_router

# 1. Inicializar la aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
"""
app = FastAPI(
    title="Sistema de Gestión de Horarios UNU",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs"
)
"""
origins = ["*"]  # Por ahora permitimos todo para desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    return {"mensaje": "Sistema de Horarios UNU - API Activa"}


"""
# 2. Configurar CORS (Permitir que Vue.js en 5173 se conecte)
origins = [
    "http://localhost:5173", # Puerto de desarrollo de Vue/Vite
    "http://127.0.0.1:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Registrar los manejadores de errores personalizados (para que la API devuelva JSON limpios)
app.add_exception_handler(CruceHorarioError, cruce_horario_handler)
app.add_exception_handler(DocenteNoDisponibleError, docente_no_disponible_handler)
# Usa un handler genérico para recursos no encontrados (ej. 404)
app.add_exception_handler(RecursoNoEncontradoError, docente_no_disponible_handler)  

# 4. Incluir el router principal (Todo el tráfico irá a /api/v1/...)
app.include_router(api_router, prefix="/api/v1")

# 5. Evento de inicio: Crear tablas al arrancar el servidor
@app.on_event("startup")
async def on_startup():
    print("Iniciando la aplicación y creando tablas...")
    # Llama a la función de database.py para sincronizar los modelos con PostgreSQL
    await create_db_and_tables() 
    print("Tablas creadas (si no existían).")
"""
