import uuid
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, TIMESTAMP, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class QrCode(Base):
    __tablename__ = "qr_codes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_id = Column(Integer, ForeignKey("tipos_qr.id"), nullable=True)
    grupo_id = Column(UUID(as_uuid=True), ForeignKey("grupos.id"), nullable=True)
    evento_id = Column(UUID(as_uuid=True), ForeignKey("eventos.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    token = Column(Text, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    
    max_usos = Column(Integer, nullable=True)
    usos_actuales = Column(Integer, default=0)
    activo = Column(Boolean, default=True)

    # Relaciones
    tipo = relationship("TipoQr")
    evento = relationship("Evento", back_populates="qrs")
    creador = relationship("Usuario")
    grupo = relationship("Grupo")

    # Replicamos los checks de tu SQL para integridad en el ORM
    __table_args__ = (
        CheckConstraint('length(token) >= 32', name='chk_token_length'),
    )