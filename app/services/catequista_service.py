from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from datetime import date, datetime
from uuid import UUID

# Modelos
from app.models.usuario import Usuario
from app.models.catequista import Catequista
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.models.telefono import Telefono
from app.models.tipo_telefono import TipoTelefono

# Utils y Schemas
from app.core.security import get_password_hash
from app.schemas.catequista import CatequistaCreate
from app.utils.email_generator import generar_email_staff

class CatequistaService:

    @staticmethod
    def create(db: Session, data: CatequistaCreate):
        # 1. Validar duplicados físicos (DNI)
        if db.query(Usuario).filter(Usuario.dni == data.dni).first():
            raise HTTPException(status_code=400, detail="El DNI ya está registrado")

        try:
            # ---------------------------------------------------
            # PASO A: Generar Email Corporativo (nombre.apellido)
            # ---------------------------------------------------
            email_base = generar_email_staff(data.nombres, data.apellidos)
            email_final = email_base
            
            # Manejo de colisiones (si hay 2 Juan Perez -> juan.perez1, juan.perez2)
            contador = 1
            while db.query(Usuario).filter(Usuario.email == email_final).first():
                user_part, domain = email_base.split('@')
                email_final = f"{user_part}{contador}@{domain}"
                contador += 1

            # ---------------------------------------------------
            # PASO B: Crear Usuario Base
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
            db.flush() # Obtenemos ID del usuario

            # ---------------------------------------------------
            # PASO C: Asignar Rol 'CATEQUISTA'
            # ---------------------------------------------------
            rol_cate = db.query(Rol).filter(Rol.nombre == "CATEQUISTA").first()
            if not rol_cate:
                raise HTTPException(status_code=500, detail="Error: Rol CATEQUISTA no existe en BD")
            
            db.add(UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=rol_cate.id))

            # ---------------------------------------------------
            # PASO D: Crear Perfil Catequista (Tabla Limpia)
            # ---------------------------------------------------
            nuevo_perfil = Catequista(
                usuario_id=nuevo_usuario.id,
                fecha_inicio=date.today(),
                especialidad="General", 
                activo=True
            )
            db.add(nuevo_perfil)

            # ---------------------------------------------------
            # PASO E: Guardar Celular en tabla 'telefonos'
            # ---------------------------------------------------
            # Buscamos el tipo 'MOVIL'
            tipo_movil = db.query(TipoTelefono).filter(TipoTelefono.codigo == "MOVIL").first()
            
            # Si no existe el tipo, podríamos crearlo o lanzar error. 
            # Aquí asumimos que tu script SQL inicial ya lo creó.
            if tipo_movil and data.celular:
                nuevo_telefono = Telefono(
                    usuario_id=nuevo_usuario.id,
                    tipo_id=tipo_movil.id,
                    numero=data.celular,
                    principal=True
                )
                db.add(nuevo_telefono)

            # ---------------------------------------------------
            # FINAL: Confirmar todo
            # ---------------------------------------------------
            db.commit()
            db.refresh(nuevo_perfil)
            
            # Construimos respuesta manual para el Out Schema
            return {
                "id": nuevo_perfil.id,
                "usuario_id": nuevo_usuario.id,
                "nombres": nuevo_usuario.nombres,
                "apellidos": nuevo_usuario.apellidos,
                "email_institucional": nuevo_usuario.email, # Devolvemos el generado
                "activo": nuevo_usuario.activo
            }

        except Exception as e:
            db.rollback()
            print(f"Error creando catequista: {e}")
            raise HTTPException(status_code=500, detail="Error interno al crear catequista")

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Catequista).options(
            joinedload(Catequista.usuario)
        ).offset(skip).limit(limit).all()