import uuid
from sqlalchemy import Column, Boolean, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # <--- Importante
from app.db.base import Base

class UsuarioRol(Base):
    __tablename__ = "usuario_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Claves foráneas
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    rol_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    asignado_por = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=True)
    
    # Auditoría y control
    asignado_en = Column(TIMESTAMP, server_default=func.now())
    activo = Column(Boolean, default=True)

    # --- RELACIONES ---

    # 1. El usuario que TIENE el rol (Dueño)
    # 'foreign_keys' es necesario porque hay dos FKs a la tabla usuarios (usuario_id y asignado_por)
    usuario = relationship("Usuario", foreign_keys=[usuario_id], back_populates="roles")

    # 2. El Rol en sí (ADMIN, CATEQUISTA...)
    rol = relationship("Rol", back_populates="asignaciones")

    # 3. El usuario que DIO el permiso (Admin) - Relación de solo lectura
    asignador = relationship("Usuario", foreign_keys=[asignado_por])