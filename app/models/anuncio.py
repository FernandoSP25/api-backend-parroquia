import uuid
from sqlalchemy import Column, String, Boolean, Text, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Anuncio(Base):
    __tablename__ = "anuncios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    titulo = Column(String(200), nullable=False)
    resumen = Column(Text, nullable=True)
    contenido = Column(Text, nullable=False)
    imagen_url = Column(Text, nullable=True)
    
    fecha_inicio = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    fecha_fin = Column(TIMESTAMP, nullable=True)
    
    publicado = Column(Boolean, default=False)
    destacado = Column(Boolean, default=False)
    orden = Column(Integer, default=0)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relaciones
    creador = relationship("Usuario")