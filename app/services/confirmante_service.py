from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime
from app.models.telefono import Telefono       
from app.models.tipo_telefono import TipoTelefono
from app.models.usuario import Usuario
from app.models.confirmante import Confirmante
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.schemas.confirmante import ConfirmanteCreateFull
from app.core.security import get_password_hash
from app.utils.email_generator import generar_email_institucional

class ConfirmanteService:

    @staticmethod
    def _agregar_celular_response(confirmantes_list):
        if not isinstance(confirmantes_list, list):
            confirmantes_list = [confirmantes_list]
            
        for conf in confirmantes_list:
            # Buscamos el telefono principal o el primero que encontremos
            if conf.usuario and conf.usuario.telefonos:
                # Prioridad: Principal=True, sino el primero
                tel = next((t.numero for t in conf.usuario.telefonos if t.principal), None)
                if not tel and len(conf.usuario.telefonos) > 0:
                    tel = conf.usuario.telefonos[0].numero
                
                # Inyectamos dinámicamente el atributo para que el Schema lo lea
                setattr(conf, 'celular', tel)
        
        return confirmantes_list[0] if len(confirmantes_list) == 1 else confirmantes_list
    
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        # Cargamos usuario Y sus teléfonos
        results = db.query(Confirmante).options(
            joinedload(Confirmante.usuario).joinedload(Usuario.telefonos)
        ).filter(Confirmante.activo == True).offset(skip).limit(limit).all()
        
        return ConfirmanteService._agregar_celular_response(results)

    @staticmethod
    def get_by_id(db: Session, confirmante_id: UUID):
        result = db.query(Confirmante).options(
            joinedload(Confirmante.usuario).joinedload(Usuario.telefonos)
        ).filter(Confirmante.id == confirmante_id).first()
        
        if result:
            return ConfirmanteService._agregar_celular_response(result)
        return None

    @staticmethod
    def create(db: Session, data: ConfirmanteCreateFull):
        try:
            # 1. Generar Email Institucional (Automático)
            email_inst = generar_email_institucional(data.nombres, data.apellidos, data.fecha_nacimiento)
            if not email_inst:
                raise HTTPException(status_code=400, detail="Datos insuficientes para generar email.")

            # Manejo de colisiones de email institucional
            email_final = email_inst
            contador = 1
            while db.query(Usuario).filter(Usuario.email == email_final).first():
                user_part, domain = email_inst.split('@')
                email_final = f"{user_part}.{contador}@{domain}"
                contador += 1

            # 2. Validar DNI (No puede repetirse)
            if db.query(Usuario).filter(Usuario.dni == data.dni).first():
                raise HTTPException(status_code=400, detail="El DNI ya existe.")
            # 3. Validar Email Personal (Si se proporciona, no puede repetirse)
            if db.query(Usuario).filter(Usuario.email_personal == data.email_personal).first():
                 raise HTTPException(status_code=400, detail="El email personal ya está en uso.")

            # 4. Crear Usuario Base
            nuevo_usuario = Usuario(
                nombres=data.nombres,
                apellidos=data.apellidos,
                dni=data.dni,
                email=email_final,              # Institucional (Login)
                email_personal=data.email_personal, # Personal (Contacto)
                password_hash=get_password_hash(data.dni),
                fecha_nacimiento=data.fecha_nacimiento,
                foto_url=data.foto_url,
                activo=True
            )
            db.add(nuevo_usuario)
            db.flush()

            # 5. Asignar Rol
            rol = db.query(Rol).filter(Rol.nombre == "CONFIRMANTE").first()
            if not rol:
                raise HTTPException(status_code=500, detail="Falta configuración de Roles.")
            if rol:
                db.add(UsuarioRol(usuario_id=nuevo_usuario.id, rol_id=rol.id))

            if data.celular:
                tipo_movil = db.query(TipoTelefono).filter(TipoTelefono.codigo == "MOVIL").first()
                # Si no existe el tipo, deberías manejarlo, aquí asumimos que existe
                if tipo_movil:
                    nuevo_telefono = Telefono(
                        usuario_id=nuevo_usuario.id,
                        tipo_id=tipo_movil.id,
                        numero=data.celular,
                        principal=True
                    )
                    db.add(nuevo_telefono)

            # 6. Crear Perfil Confirmante
            nuevo_confirmante = Confirmante(
                usuario_id=nuevo_usuario.id,
                # Familia
                apoderado_nombre=data.apoderado_nombre,
                apoderado_telefono=data.apoderado_telefono,
                apoderado_email=data.apoderado_email,
                apoderado_relacion=data.apoderado_relacion,
                # Sacramentos
                bautizado=data.bautizado,
                parroquia_bautismo=data.parroquia_bautismo,
                fecha_bautismo=data.fecha_bautismo,
                libro_bautismo=data.libro_bautismo,
                folio_bautismo=data.folio_bautismo,
                # Padrinos
                nombre_padrino=data.nombre_padrino,
                telefono_padrino=data.telefono_padrino,
                email_padrino=data.email_padrino,
                
                activo=True
            )
            db.add(nuevo_confirmante)
            db.commit()
            db.refresh(nuevo_confirmante)
            setattr(nuevo_confirmante, 'celular', data.celular)
            return nuevo_confirmante

        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            print(f"Error Create Confirmante: {e}")
            raise HTTPException(status_code=500, detail="Error interno al crear confirmante.")

