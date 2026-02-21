from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class IpBloqueada(Base):
    __tablename__ = "ips_bloqueadas"

    id = Column(Integer, primary_key=True)
    bloqueado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    ip_address = Column(INET, unique=True, nullable=False)
    razon = Column(Text, nullable=True)
    
    bloqueado_en = Column(TIMESTAMP, server_default=func.now())
    expira_en = Column(TIMESTAMP, nullable=True)

    # Relaciones
    admin = relationship("Usuario")