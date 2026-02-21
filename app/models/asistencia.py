import uuid
from sqlalchemy import Column, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id", ondelete="CASCADE"), nullable=False)
    qr_id = Column(UUID(as_uuid=True), ForeignKey("qr_codes.id"), nullable=True)
    registrada_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    fecha = Column(TIMESTAMP, server_default=func.now())
    metodo = Column(String(20), default='QR') # 'QR', 'MANUAL'
    observaciones = Column(Text, nullable=True)
    ip_address = Column(INET, nullable=True)

    # Relaciones
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="asistencias")
    evento = relationship("Evento", back_populates="asistencias")
    qr = relationship("QrCode")
    registrador = relationship("Usuario", foreign_keys=[registrada_por])