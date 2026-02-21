from sqlalchemy.orm import Session
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import joinedload

from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.models.telefono import Telefono
from app.models.tipo_telefono import TipoTelefono
from app.core.security import get_password_hash
from app.utils.email_generator import generar_email_institucional


class UsuarioService:

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Usuario).options(
            joinedload(Usuario.roles).joinedload(UsuarioRol.rol),
            joinedload(Usuario.telefonos)   
        ).order_by(Usuario.created_at.desc()
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, user_id: UUID):
        return db.query(Usuario).options(
            joinedload(Usuario.roles).joinedload(UsuarioRol.rol),
            joinedload(Usuario.telefonos) 
        ).filter(
            Usuario.id == user_id,
            Usuario.deleted_at == None
        ).first()

    @staticmethod
    def get_by_email(db: Session, email: str):
        return db.query(Usuario).filter(
            Usuario.email == email,
            Usuario.deleted_at == None
        ).first()

    @staticmethod
    def create(db: Session, data: UsuarioCreate):
        # =====================================================
        # 1. AUTOGENERAR EMAIL INSTITUCIONAL SI NO VIENE
        # =====================================================
        email_final = data.email

        if not email_final and data.nombres and data.apellidos and data.fecha_nacimiento:
            email_final = generar_email_institucional(
                data.nombres,
                data.apellidos,
                data.fecha_nacimiento
            )

        if not email_final:
            raise HTTPException(
                status_code=400,
                detail="No se pudo generar el email institucional. Faltan datos."
            )

        # =====================================================
        # 2. VALIDAR DUPLICADOS (EMAIL O DNI)
        # =====================================================
        existing_user = db.query(Usuario).filter(
            or_(
                Usuario.email == email_final,
                Usuario.dni == data.dni
            )
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="El DNI o el email ya está registrado en el sistema."
            )

        # =====================================================
        # 3. CREAR USUARIO
        # =====================================================
        db_obj = Usuario(
            nombres=data.nombres,
            apellidos=data.apellidos,
            email=email_final,                  # 👈 usamos el generado
            email_personal=data.email_personal, # gmail / hotmail
            dni=data.dni,
            password_hash=get_password_hash(data.password),
            activo=data.activo,
            fecha_nacimiento=data.fecha_nacimiento,
            foto_url=data.foto_url
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def update(db: Session, user: Usuario, data: UsuarioUpdate):
        # 1. Separamos datos especiales (password y celular) del resto
        update_data = data.model_dump(exclude_unset=True)
        
        # --- A. Actualización de Password ---
        if "password" in update_data:
            if update_data["password"]: # Solo si enviaron algo
                update_data["password_hash"] = get_password_hash(update_data.pop("password"))
            else:
                # Si enviaron cadena vacía, la quitamos para no borrar el hash actual
                update_data.pop("password")

        # --- B. Actualización de Celular (Tabla 'telefonos') ---
        # Si 'celular' viene en el JSON, hay que actualizar la relación
        if "celular" in update_data:
            nuevo_celular = update_data.pop("celular")
            
            # Buscamos el tipo 'MOVIL'
            tipo_movil = db.query(TipoTelefono).filter(TipoTelefono.codigo == "MOVIL").first()
            
            if tipo_movil and nuevo_celular:
                # Buscamos si el usuario ya tiene un celular registrado
                telefono_obj = db.query(Telefono).filter(
                    Telefono.usuario_id == user.id,
                    Telefono.tipo_id == tipo_movil.id
                ).first()

                if telefono_obj:
                    # Si existe, actualizamos
                    telefono_obj.numero = nuevo_celular
                else:
                    # Si no existe, creamos uno nuevo
                    nuevo_telf = Telefono(
                        usuario_id=user.id,
                        tipo_id=tipo_movil.id,
                        numero=nuevo_celular,
                        principal=True
                    )
                    db.add(nuevo_telf)

        # --- C. Actualización de Datos Base (Usuario) ---
        for field, value in update_data.items():
            # Seguridad: Evitamos que cambien el ID o campos de auditoría manualmente
            if hasattr(user, field) and field not in ['id', 'created_at', 'password_hash']:
                setattr(user, field, value)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error al actualizar usuario: {str(e)}")

    @staticmethod
    def desactivar(db: Session, user_id: UUID, admin_id: UUID = None):
        """
        Acción: POST /usuarios/{id}/desactivar
        Bloquea el acceso al sistema.
        """
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Lógica de negocio
        user.activo = False
        user.deleted_at = datetime.now()
        user.deleted_by = admin_id # Opcional: para saber quién lo borró

        # Si quieres, aquí podrías desactivar también sus perfiles relacionados (Confirmante/Catequista)
        # pero con desactivar el Usuario ya no pueden hacer login.
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Usuario desactivado correctamente", "activo": False}

    @staticmethod
    def reactivar(db: Session, user_id: UUID):
        """
        Acción: POST /usuarios/{id}/reactivar
        Restaura el acceso al sistema.
        """
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        # Lógica de negocio
        user.activo = True
        user.deleted_at = None
        user.deleted_by = None

        db.add(user)
        db.commit()
        db.refresh(user)
        return {"message": "Usuario reactivado correctamente", "activo": True}