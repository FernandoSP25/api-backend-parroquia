import sys
import os
import uuid
# --- CORRECCIÓN DE PATH ---
# 1. Obtenemos la ruta absoluta de ESTE archivo (crear_admin.py)
current_script_path = os.path.abspath(__file__)

# 2. Obtenemos el directorio donde está el script (.../app/scritps)
script_dir = os.path.dirname(current_script_path)

# 3. Subimos DOS niveles para llegar a la raíz del proyecto
#    (De 'scripts' sube a 'app', y de 'app' sube a 'api_parroquia_sjmv')
project_root = os.path.abspath(os.path.join(script_dir, "../../"))

# 4. Agregamos esa raíz al sistema de Python
sys.path.append(project_root)
# ---------------------------

# Ahora sí funcionarán los imports
from sqlalchemy.orm import Session
from app.db.session import SessionLocal 
from app.services import usuario_service
from app.schemas.usuario import UsuarioCreate
from app.models.usuario import Usuario
from app.models.rol import UsuarioRol # Importamos el modelo de la tabla intermedia

def crear_admin_con_rol():
    db: Session = SessionLocal()
    try:
        # 1. DATOS FIJOS (Tus IDs de la BD)
        # ID del Rol ADMIN que me diste:
        ID_ROL_ADMIN = uuid.UUID("99bff7d2-b809-44af-b8f7-a29cd8d32b5a") 
        EMAIL_ADMIN = "admin@parroquia.com"

        print(f"🚀 Iniciando proceso para: {EMAIL_ADMIN}")

        # 2. BUSCAR O CREAR USUARIO
        usuario = db.query(Usuario).filter(Usuario.email == EMAIL_ADMIN).first()

        if not usuario:
            print("👤 Creando usuario en tabla 'usuarios'...")
            nuevo_usuario = UsuarioCreate(
                nombre="Administrador Principal",
                email=EMAIL_ADMIN,
                dni="00000000",
                password="AdminPassword123!", # ¡Cámbiala!
                fecha_nacimiento="1990-01-01",
                activo=True
            )
            usuario = usuario_service.create(db, nuevo_usuario)
            print(f"✅ Usuario creado con ID: {usuario.id}")
        else:
            print(f"ℹ️ El usuario ya existe (ID: {usuario.id})")

        # 3. ASIGNAR EL ROL (Tabla usuario_roles)
        # Verificamos si ya tiene ese rol asignado para no duplicar error
        asignacion = db.query(UsuarioRol).filter(
            UsuarioRol.usuario_id == usuario.id,
            UsuarioRol.rol_id == ID_ROL_ADMIN
        ).first()

        if not asignacion:
            print(f"🔗 Asignando rol ADMIN ({ID_ROL_ADMIN}) al usuario...")
            nueva_asignacion = UsuarioRol(
                usuario_id=usuario.id,
                rol_id=ID_ROL_ADMIN,
                asignado_por=usuario.id # Se auto-asigna al inicio
            )
            db.add(nueva_asignacion)
            db.commit()
            print("✅ ¡Rol asignado exitosamente!")
        else:
            print("✅ El usuario ya tenía el rol ADMIN.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_admin_con_rol()