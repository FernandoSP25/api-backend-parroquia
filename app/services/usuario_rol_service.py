from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.usuario_rol import UsuarioRol
from app.schemas.usuario_rol import UsuarioRolCreate

class UsuarioRolService:

    @staticmethod
    def create(db: Session, data: UsuarioRolCreate, admin_id: UUID):
        # 1. Verificar si ya existe esa asignación
        existing = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == data.usuario_id,
            UsuarioRol.rol_id == data.rol_id
        ).first()

        if existing:
            # Si existe pero estaba inactivo, lo reactivamos
            if not existing.activo:
                existing.activo = True
                existing.asignado_por = admin_id
                db.commit()
                db.refresh(existing)
                return existing
            # Si ya está activo, lanzamos error o devolvemos el existente
            raise HTTPException(status_code=400, detail="El usuario ya tiene este rol asignado.")

        # 2. Crear nueva asignación
        nuevo_rol = UsuarioRol(
            usuario_id=data.usuario_id,
            rol_id=data.rol_id,
            asignado_por=admin_id,
            activo=True
        )
        db.add(nuevo_rol)
        db.commit()
        db.refresh(nuevo_rol)
        return nuevo_rol

    @staticmethod
    def get_by_usuario_id(db: Session, usuario_id: UUID):
        return db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.activo == True
        ).all()

    @staticmethod
    def soft_delete(db: Session, usuario_id: UUID, rol_id: UUID):
        registro = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id
        ).first()

        if not registro:
            raise HTTPException(status_code=404, detail="Asignación no encontrada")
        
        registro.activo = False
        db.commit()
        return registro 