import uuid
from sqlalchemy import Column, String, Boolean, Date, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    # --- COLUMNAS PRINCIPALES (ACTUALIZADO) ---
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # NUEVO: Separación de nombres y apellidos
    nombres = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    
    dni = Column(String(15), unique=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=True)
    foto_url = Column(Text, nullable=True)

    # NUEVO: Manejo de doble correo
    email = Column(String(150), unique=True, nullable=False) # Para Login
    email_personal = Column(String(150), nullable=True)      # Para Contacto
    
    password_hash = Column(Text, nullable=False)

    # --- CONTROL Y AUDITORÍA ---
    activo = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP, nullable=True)
    deleted_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # ==========================================
    #            RELACIONES (JOINs)
    # ==========================================

    # 1. PERFILES
    catequista_perfil = relationship("Catequista", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    confirmante_perfil = relationship("Confirmante", back_populates="usuario", uselist=False, cascade="all, delete-orphan")

    # 2. DATOS DE CONTACTO
    direccion_relacion = relationship("Direccion", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    telefonos = relationship("Telefono", back_populates="usuario", cascade="all, delete-orphan")

    # 3. SEGURIDAD Y ROLES
    roles = relationship(
        "UsuarioRol", 
        back_populates="usuario", 
        cascade="all, delete-orphan",
        foreign_keys="[UsuarioRol.usuario_id]" 
    )
    
    sesiones = relationship("Sesion", back_populates="usuario", cascade="all, delete-orphan")
    password_history = relationship("PasswordHistory", back_populates="usuario", cascade="all, delete-orphan")

    # 4. OPERACIÓN DIARIA
    notificaciones = relationship("Notificacion", back_populates="usuario", cascade="all, delete-orphan")
    
    asistencias = relationship(
        "Asistencia", 
        back_populates="usuario", 
        cascade="all, delete-orphan",
        foreign_keys="[Asistencia.usuario_id]"
    )

    logs_acceso = relationship("LogAcceso", back_populates="usuario")

    # Propiedad útil para devolver el nombre completo si lo necesitas
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def celular(self):
        """
        Propiedad mágica: busca en la lista de teléfonos cargada
        y devuelve el número principal o el primero que encuentre.
        """
        if not self.telefonos:
            return None
        
        # Prioridad 1: Buscar el que tenga principal=True
        for t in self.telefonos:
            if t.principal:
                return t.numero
        
        # Prioridad 2: Devolver el primero de la lista
        return self.telefonos[0].numero