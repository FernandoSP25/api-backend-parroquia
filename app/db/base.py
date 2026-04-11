from sqlalchemy.ext.declarative import declarative_base

# 1. DEFINIMOS LA CLASE BASE
Base = declarative_base()

# 2. IMPORTAMOS LOS MODELOS PARA ALEMBIC
# Importaciones existentes
from app.models.tipo_evento import TipoEvento
from app.models.usuario import Usuario
from app.models.evento import Evento

from app.models.estado_asistencia import EstadoAsistencia
