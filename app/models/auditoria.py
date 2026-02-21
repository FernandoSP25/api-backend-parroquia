from sqlalchemy import Column, String, BigInteger, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Auditoria(Base):
    __tablename__ = "auditoria"

    id = Column(BigInteger, primary_key=True) # Es BIGSERIAL en la BD
    
    tabla = Column(String(50), nullable=False)
    registro_id = Column(UUID(as_uuid=True), nullable=False)
    accion = Column(String(10), nullable=False) # INSERT, UPDATE, DELETE
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    valores_anteriores = Column(JSONB, nullable=True)
    valores_nuevos = Column(JSONB, nullable=True)
    
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    fecha = Column(TIMESTAMP, server_default=func.now())

    # Relaciones
    usuario = relationship("Usuario")