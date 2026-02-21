from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# 1. CREAR EL MOTOR (ENGINE)
# Usamos la URL que definiste en settings.SQLALCHEMY_DATABASE_URI
# pool_pre_ping=True ayuda a evitar errores de "conexión perdida"
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# 2. CREAR LA FÁBRICA DE SESIONES (SESSIONLOCAL)
# Cada vez que un usuario haga una petición, usaremos esto para crear una sesión temporal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)