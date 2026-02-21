import uuid
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Configuracion(Base):
    __tablename__ = "configuraciones"

    clave = Column(String(100), primary_key=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    valor = Column(Text, nullable=False)
    tipo = Column(String(20), nullable=False) # 'string', 'number', 'boolean', 'json'
    descripcion = Column(Text, nullable=True)
    categoria = Column(String(50), nullable=True)
    modificable = Column(Boolean, default=True)
    
    updated_at = Column(TIMESTAMP, server_default=func.now())

    # Relaciones
    editor = relationship("Usuario")