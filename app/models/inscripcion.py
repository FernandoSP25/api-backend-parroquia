import enum
# CAMBIO: Importamos String en lugar de Enum de SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

# Mantenemos esto para usarlo en Python (validación), 
# pero ya no forzamos a la BD a usarlo como tipo.
class EstadoInscripcion(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    CONTACTADO = "CONTACTADO"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"

class Inscripcion(Base):
    __tablename__ = "inscripciones"

    # En SQLAlchemy, 'Integer' con 'primary_key=True' 
    # detecta automáticamente que en Postgres debe usar SERIAL. No hay que cambiar nada aquí.
    id = Column(Integer, primary_key=True, index=True) # Postgres lo tratará como SERIAL

    # --- Sección 1: Datos del Joven ---
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    dni = Column(String(8), unique=True, nullable=False, index=True)
    fecha_nacimiento = Column(Date, nullable=False)
    edad = Column(Integer, nullable=False)
    direccion = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    celular_joven = Column(String(20), nullable=False)

    # --- Sección 2: Datos del Apoderado ---
    nombre_apoderado = Column(String(100), nullable=False)
    celular_apoderado = Column(String(20), nullable=False)

    # --- Sección 3: Gestión Interna ---
    # CAMBIO CRÍTICO AQUÍ:
    # Usamos String(20) para coincidir con tu VARCHAR(20) de SQL.
    # Ponemos default="PENDIENTE" como texto simple.
    estado = Column(String(20), default="PENDIENTE") 
    
    fecha_registro = Column(TIMESTAMP, server_default=func.now())
    notas_internas = Column(Text, nullable=True)