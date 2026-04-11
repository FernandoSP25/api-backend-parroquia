# app/models/__init__.py

from .usuario import Usuario
from .rol import Rol
from .usuario_rol import UsuarioRol
from .tipo_evento import TipoEvento
from .tipo_telefono import TipoTelefono

# --- AGREGA ESTOS NUEVOS QUE CREASTE ---
from .sesion import Sesion
from .notificacion import Notificacion
from .password_history import PasswordHistory
from .log_acceso import LogAcceso
from .nota import Nota
from .evento import Evento
from .asistencia import Asistencia
from .anuncio import Anuncio
from .configuracion import Configuracion
from .auditoria import Auditoria
from .direccion import Direccion
from .telefono import Telefono
from .catequista import Catequista
from .confirmante import Confirmante
from .grupo import Grupo
from .anio_catequetico import AnioCatequetico
from .ip_bloqueada import IpBloqueada
from .grupo import Grupo
from .catequista_grupo import CatequistaGrupo
from .estado_asistencia import EstadoAsistencia
