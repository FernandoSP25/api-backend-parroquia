from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text # Para hacer consultas SQL puras de prueba

# Importaciones de tu proyecto
from app.core.config import settings     
from app.db.session import engine         
from app.db.base import Base              
from app.dependencies.database import get_db 

from app.routers import (
    auth, 
    usuarios, 
    tipo_evento, 
    tipos_telefono,
    catequistas,   
    confirmantes,  
    grupos,       
    eventos,       
    asistencias,   
    roles,
    usuario_roles,
    direcciones,
    telefonos,
    notas,
    anuncios,
    inscripciones,
    admin,
    anios_catequeticos,
    dashboard
)

from fastapi.middleware.cors import CORSMiddleware # <--- IMPORTAR ESTO
# --- PASO 1: CREACIÓN DE TABLAS (Mágico para desarrollo) ---
# Esta línea le dice a SQLAlchemy: "Mira todos los modelos importados en db.base 
# y crea las tablas en PostgreSQL si no existen".
#Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API del Sistema Parroquial"
)

origins = [
    "http://localhost:3000", # El puerto de tu Next.js
    "http://127.0.0.1:3000",
    "http://192.168.1.4:3000",
    "https://confirmacion-sjmv.vercel.app" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permitir todos los headers (Authorization, etc.)
)
# -

# --- PASO 2: VERIFICACIÓN DE CONEXIÓN (Endpoint de prueba) ---
@app.get("/check-db")
def health_check_db(db: Session = Depends(get_db)):
    """
    Endpoint para probar si la API puede hablar con PostgreSQL.
    Si ves el mensaje de éxito, ¡ya ganaste!
    """
    try:
        # Hacemos una consulta tonta "SELECT 1" solo para ver si responde
        db.execute(text("SELECT 1"))
        return {
            "estado": "Conectado 🟢", 
            "mensaje": "¡La API y PostgreSQL son amigos! Todo listo."
        }
    except Exception as e:
        # Si falla, te dirá exactamente por qué (contraseña mal, puerto cerrado, etc.)
        return {
            "estado": "Error 🔴", 
            "error": str(e)
        }

@app.get("/")
def root():
    return {"mensaje": "Bienvenido a la API Parroquial v1"}

# --- AQUÍ REGISTRARÁS TUS ROUTERS DESPUÉS ---
# from routers import users, auth


app.include_router(tipo_evento.router, prefix=settings.API_V1_STR)
app.include_router(tipos_telefono.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(usuarios.router, prefix=settings.API_V1_STR)
app.include_router(catequistas.router, prefix=settings.API_V1_STR)
app.include_router(confirmantes.router, prefix=settings.API_V1_STR)
app.include_router(roles.router, prefix=settings.API_V1_STR)
app.include_router(usuario_roles.router, prefix=settings.API_V1_STR)
app.include_router(direcciones.router, prefix=settings.API_V1_STR)
app.include_router(telefonos.router, prefix=settings.API_V1_STR)
app.include_router(inscripciones.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(grupos.router, prefix=settings.API_V1_STR)
app.include_router(eventos.router, prefix=settings.API_V1_STR)
app.include_router(anios_catequeticos.router, prefix=settings.API_V1_STR)
app.include_router(asistencias.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)