import uuid
from sqlalchemy import Column, String, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    
    token_hash = Column(Text, unique=True, nullable=False)
    refresh_token_hash = Column(Text, unique=True, nullable=True)
    
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    dispositivo = Column(String(100), nullable=True)
    ubicacion = Column(String(200), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    expires_at = Column(TIMESTAMP, nullable=False)
    last_activity = Column(TIMESTAMP, server_default=func.now())
    
    revoked = Column(Boolean, default=False)
    revoked_at = Column(TIMESTAMP, nullable=True)
    revoked_reason = Column(Text, nullable=True)

    # Relación inversa
    usuario = relationship("Usuario", back_populates="sesiones")