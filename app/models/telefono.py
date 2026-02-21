import uuid
from sqlalchemy import Column, String, Boolean, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Telefono(Base):
    __tablename__ = "telefonos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos_telefono.id"), nullable=False)
    
    numero = Column(String(20), nullable=False)
    extension = Column(String(10), nullable=True)
    principal = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario", back_populates="telefonos")
    tipo = relationship("TipoTelefono", back_populates="telefonos")