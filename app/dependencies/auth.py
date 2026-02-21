from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.dependencies.database import get_db
# IMPORTANTE: Importamos la CLASE UsuarioService
from app.services.usuario_service import UsuarioService 
from app.models.usuario import Usuario
from app.schemas.auth import TokenData

# Ajusta esto si tu prefijo cambia
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# 1. Obtener Usuario Actual (Sin 'async' porque usamos Session normal)
def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        token_data = TokenData(id=user_id_str)
    except JWTError:
        raise credentials_exception

    # CORRECCIÓN AQUÍ: Usamos UsuarioService.get_by_id (Clase estática)
    user = UsuarioService.get_by_id(db, user_id=UUID(token_data.id))
    
    if user is None:
        raise credentials_exception
        
    return user

# 2. Validar que esté ACTIVO
def get_current_active_user(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

# 3. Verificador de Roles (RoleChecker)
class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    # Sin 'async'
    def __call__(self, user: Usuario = Depends(get_current_active_user)):
        """
        Verifica si el usuario tiene permiso.
        Usamos la relación 'user.roles' que definimos en el modelo Usuario.
        """
        # Extraemos los nombres de los roles activos del usuario
        # user.roles es una lista de objetos UsuarioRol
        # ur.rol.nombre accede al nombre (ej: "ADMIN")
        user_roles = [ur.rol.nombre for ur in user.roles if ur.activo]
        
        # Si es ADMIN, pase VIP automático (Opcional, pero recomendado)
        if "ADMIN" in user_roles:
            return user

        # Verificamos si tiene al menos uno de los roles permitidos
        has_permission = any(rol in self.allowed_roles for rol in user_roles)
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tienes permisos suficientes. Requerido: {self.allowed_roles}"
            )
        return user