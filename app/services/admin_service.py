from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date

# Modelos
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.models.telefono import Telefono
from app.models.tipo_telefono import TipoTelefono

# Utils y Schemas
from app.core.security import get_password_hash
from app.schemas.admin import AdminCreate
from app.utils.email_generator import generar_email_staff

class AdminService:

    @staticmethod
    def create(db: Session, data: AdminCreate):
        # 1. Validar duplicados físicos
        if db.query(Usuario).filter((Usuario.email == data.email_personal) | (Usuario.dni == data.dni)).first():
            raise HTTPException(status_code=400, detail="El DNI o Email Personal ya están registrados")

        try:
            # ---------------------------------------------------
            # PASO 1: Generar Email Corporativo (nombre.apellido)
            # ---------------------------------------------------
            email_base = generar_email_staff(data.nombres, data.apellidos)
            email_final = email_base
            
            # Manejo de colisiones
            contador = 1
            while db.query(Usuario).filter(Usuario.email == email_final).first():
                user_part, domain = email_base.split('@')
                email_final = f"{user_part}{contador}@{domain}"
                contador += 1

            # ---------------------------------------------------
            # PASO 2: Crear Usuario Base
            # ---------------------------------------------------
            nuevo_usuario = Usuario(
                nombres=data.nombres,
                apellidos=data.apellidos,
                dni=data.dni,
                fecha_nacimiento=data.fecha_nacimiento,
                
                # Credenciales
                email=email_final,                  # Login generado
                email_personal=data.email_personal, # Contacto
                password_hash=get_password_hash(data.password), # Password MANUAL
                
                activo=True
            )
            db.add(nuevo_usuario)
            db.flush() 

            # ---------------------------------------------------
            # PASO 3: Asignar Rol 'ADMIN'
            # ---------------------------------------------------
            rol_admin = db.query(Rol).filter(Rol.nombre == "ADMIN").first()
            if not rol_admin:
                raise HTTPException(status_code=500, detail="Rol ADMIN no configurado en BD")
            
            db.add(UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=rol_admin.id))

            # ---------------------------------------------------
            # PASO 4: Guardar Celular (Tabla Telefonos)
            # ---------------------------------------------------
            tipo_movil = db.query(TipoTelefono).filter(TipoTelefono.codigo == "MOVIL").first()
            
            if tipo_movil and data.celular:
                nuevo_telefono = Telefono(
                    usuario_id=nuevo_usuario.id,
                    tipo_id=tipo_movil.id,
                    numero=data.celular,
                    principal=True
                )
                db.add(nuevo_telefono)

            # ---------------------------------------------------
            # FINAL: Confirmar
            # ---------------------------------------------------
            db.commit()
            db.refresh(nuevo_usuario)
            
            return {
                "id": nuevo_usuario.id,
                "nombres": nuevo_usuario.nombres,
                "apellidos": nuevo_usuario.apellidos,
                "email_institucional": nuevo_usuario.email,
                "activo": nuevo_usuario.activo
            }

        except Exception as e:
            db.rollback()
            print(f"Error creando admin: {e}")
            raise HTTPException(status_code=500, detail="Error interno al crear administrador")