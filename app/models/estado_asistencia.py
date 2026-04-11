from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class EstadoAsistencia(Base):
    __tablename__ = "estados_asistencia"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())