import uuid
from sqlalchemy import Column, Integer, Date, Text, Boolean, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class AnioCatequetico(Base):
    __tablename__ = "anios_catequeticos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    anio = Column(Integer, unique=True, nullable=False) # Ej: 2026
    fecha_inicio = Column(Date, nullable=True)
    fecha_fin = Column(Date, nullable=True)
    descripcion = Column(Text, nullable=True)
    
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # --- RELACIONES ---
    
    # 1. Grupos que pertenecen a este año
    grupos = relationship("Grupo", back_populates="anio")
    
    # 2. Confirmantes inscritos en este año (historial académico)
    confirmantes = relationship("Confirmante", back_populates="anio")