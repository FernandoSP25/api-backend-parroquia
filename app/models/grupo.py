import uuid
from sqlalchemy import Column, String, Integer, Text, Boolean, ForeignKey, TIMESTAMP, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Grupo(Base):
    __tablename__ = "grupos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    nombre = Column(String(50), nullable=False)
    anio_id = Column(UUID(as_uuid=True), ForeignKey("anios_catequeticos.id"), nullable=True)
    
    descripcion = Column(Text, nullable=True)
    capacidad_maxima = Column(Integer, default=30)
    
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Restricción Unique (nombre, anio_id) definida en SQL
    __table_args__ = (
        UniqueConstraint('nombre', 'anio_id', name='uq_grupo_nombre_anio'),
    )

    # --- RELACIONES ---
    
    # 1. Año al que pertenece
    anio = relationship("AnioCatequetico", back_populates="grupos")
    
    # 2. Confirmantes en este grupo
    confirmantes = relationship("Confirmante", back_populates="grupo")
    
    # 3. Eventos exclusivos de este grupo
    eventos = relationship("Evento", back_populates="grupo")

    # 4. Catequistas asignados (Tabla intermedia)
    catequistas_asignados = relationship("CatequistaGrupo", back_populates="grupo")
    
    # 5. QRs vinculados al grupo
    qrs = relationship("QrCode", back_populates="grupo")