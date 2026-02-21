from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.models.usuario import Usuario
from app.schemas.rol import RolCreate, RolAsignacionRequest

class RolService:
    
    # 1. LISTAR TODOS LOS ROLES (Para el combobox del Frontend)
    @staticmethod
    def get_all_roles(db: Session):
        return db.query(Rol).filter(Rol.activo == True).all()

    # 2. BUSCAR ROL POR NOMBRE (Útil para lógica interna)
    @staticmethod
    def get_by_name(db: Session, nombre: str):
        return db.query(Rol).filter(Rol.nombre == nombre).first()

    # 3. CREAR UN ROL (Solo para admins)
    @staticmethod
    def create_rol(db: Session, role_in: RolCreate):
        rol = Rol(
            nombre=role_in.nombre.upper(), # Guardamos siempre en mayúsculas
            descripcion=role_in.descripcion,
            activo=role_in.activo
        )
        db.add(rol)
        db.commit()
        db.refresh(rol)
        return rol

    # 4. ASIGNAR ROL A USUARIO (La parte más importante)
    @staticmethod
    def asignar_rol(db: Session, data: RolAsignacionRequest, admin_id: UUID):
        # Verificar que el usuario existe
        user = db.query(Usuario).filter(Usuario.id == data.usuario_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Verificar que el rol existe
        rol = db.query(Rol).filter(Rol.id == data.rol_id).first()
        if not rol:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        # Verificar si ya tiene el rol asignado (aunque esté inactivo)
        asignacion_existente = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == data.usuario_id,
            UsuarioRol.rol_id == data.rol_id
        ).first()

        if asignacion_existente:
            if asignacion_existente.activo:
                raise HTTPException(status_code=400, detail="El usuario ya tiene este rol activo")
            else:
                # Si existía pero estaba inactivo, lo reactivamos
                asignacion_existente.activo = True
                asignacion_existente.asignado_por = admin_id
                db.commit()
                db.refresh(asignacion_existente)
                return asignacion_existente
        
        # Si no existe, creamos la relación
        nueva_asignacion = UsuarioRol(
            usuario_id=data.usuario_id,
            rol_id=data.rol_id,
            asignado_por=admin_id,
            activo=True
        )
        db.add(nueva_asignacion)
        db.commit()
        db.refresh(nueva_asignacion)
        return nueva_asignacion

    # 5. OBTENER ROLES DE UN USUARIO (Con detalles bonitos)
    @staticmethod
    def get_user_roles(db: Session, usuario_id: UUID):
        # Hacemos un JOIN para traer el nombre del rol directamente
        results = db.query(UsuarioRol, Rol).join(Rol, UsuarioRol.rol_id == Rol.id)\
            .filter(UsuarioRol.usuario_id == usuario_id, UsuarioRol.activo == True).all()
        
        # Formateamos la salida para el Schema UsuarioRolOut
        lista_roles = []
        for user_rol, rol_data in results:
            lista_roles.append({
                "id": user_rol.id,
                "rol_id": rol_data.id,
                "rol_nombre": rol_data.nombre,
                "rol_descripcion": rol_data.descripcion,
                "asignado_en": user_rol.asignado_en,
                "activo": user_rol.activo
            })
        return lista_roles

    # 6. REVOCAR ROL (Desasignar)
    @staticmethod
    def revocar_rol(db: Session, usuario_id: UUID, rol_id: UUID):
        asignacion = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario_id,
            UsuarioRol.rol_id == rol_id
        ).first()

        if not asignacion:
            raise HTTPException(status_code=404, detail="Asignación de rol no encontrada")
        
        asignacion.activo = False # Soft delete
        db.commit()
        return {"message": "Rol revocado correctamente"}