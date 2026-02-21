from sqlalchemy.orm import Session
from app.models.usuario import Usuario
from app.models.rol import Rol
from app.models.usuario_rol import UsuarioRol
from app.core.security import verify_password

def authenticate_user(db: Session, email: str, password: str):
    """
    Busca un usuario por email y verifica su contraseña.
    Retorna el objeto Usuario si es válido, o None si falla.
    """
    # 1. Búsqueda eficiente: El campo 'email' tiene índice UNIQUE en tu modelo.
    #    Esto garantiza una búsqueda O(1) o O(log n) en base de datos.
    user = db.query(Usuario).filter(
        Usuario.email == email,
        Usuario.deleted_at.is_(None)  # REGLA: No loguear usuarios eliminados
    ).first()

    # 2. Si no existe el usuario, retornamos None (falla autenticación)
    if not user:
        return None

    # 3. REGLA: Verificar si el usuario está activo (banneado/desactivado)
    if not user.activo:
        return None

    # 4. Comparación Criptográfica:
    #    Aquí es donde 'verify_password' toma el texto plano y lo compara 
    #    contra el hash bcrypt de la BD. 
    if not verify_password(password, user.password_hash):
        return None

    return user

def get_user_roles(db: Session, user_id) -> list[str]:
    """
    Obtiene la lista de NOMBRES de roles activos para un usuario.
    Ejemplo de retorno: ['ADMINISTRADOR', 'CATEQUISTA']
    """
    # Hacemos un JOIN entre Rol y UsuarioRol
    roles = db.query(Rol.nombre).join(
        UsuarioRol, UsuarioRol.rol_id == Rol.id
    ).filter(
        UsuarioRol.usuario_id == user_id,
        UsuarioRol.activo == True, # Solo asignaciones activas
        Rol.activo == True         # Solo roles activos
    ).all()
    
    # SQLAlchemy devuelve tuplas [('ADMIN',), ('OTRO',)], las convertimos a lista plana
    return [r[0] for r in roles]