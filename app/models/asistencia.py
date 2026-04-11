import uuid
from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id", ondelete="CASCADE"), nullable=False)
    
    # 3 = "FALTA" por defecto (según insertamos en el script SQL)
    estado_id = Column(Integer, ForeignKey("estados_asistencia.id"), nullable=False, default=3) 
    
    fecha = Column(TIMESTAMP, server_default=func.now())
    observaciones = Column(Text, nullable=True)
    registrada_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    ip_address = Column(INET, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="asistencias")
    evento = relationship("Evento", back_populates="asistencias")
    registrador = relationship("Usuario", foreign_keys=[registrada_por])
    estado = relationship("EstadoAsistencia")