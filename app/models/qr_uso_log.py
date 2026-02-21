import uuid
from sqlalchemy import Column, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class QrUsoLog(Base):
    __tablename__ = "qr_uso_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qr_id = Column(UUID(as_uuid=True), ForeignKey("qr_codes.id"), nullable=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=True)
    
    exitoso = Column(Boolean, nullable=False)
    razon_fallo = Column(Text, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())

    # Relaciones
    qr = relationship("QrCode")
    usuario = relationship("Usuario")
    evento = relationship("Evento")