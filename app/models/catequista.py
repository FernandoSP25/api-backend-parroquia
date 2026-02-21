import uuid
from sqlalchemy import Column, String, Boolean, Text, Date, ForeignKey, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Catequista(Base):
    __tablename__ = "catequistas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Relación 1 a 1 con Usuario
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    especialidad = Column(Text, nullable=True)
    biografia = Column(Text, nullable=True)
    fecha_inicio = Column(Date, nullable=True)
    
    # Mapeo de array de texto (TEXT[])
    certificaciones = Column(ARRAY(Text), nullable=True)
    
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="catequista_perfil")
    grupos_asignados = relationship("CatequistaGrupo", back_populates="catequista") 