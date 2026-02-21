from sqlalchemy import Column, String, Boolean, Text, ForeignKey, TIMESTAMP, BigInteger
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class LogAcceso(Base):
    __tablename__ = "logs_acceso"

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    accion = Column(String(50), nullable=False) # 'login', 'logout', 'failed_login'
    exitoso = Column(Boolean, default=True)
    
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    dispositivo = Column(String(100), nullable=True)
    ubicacion = Column(String(200), nullable=True)
    razon_fallo = Column(Text, nullable=True)
    
    timestamp = Column(TIMESTAMP, server_default=func.now())

    # Relación inversa
    usuario = relationship("Usuario", back_populates="logs_acceso")