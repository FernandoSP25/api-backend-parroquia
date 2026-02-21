from sqlalchemy.ext.declarative import declarative_base

# 1. DEFINIMOS LA CLASE BASE
Base = declarative_base()

# 2. IMPORTAMOS LOS MODELOS PARA ALEMBIC
# Importaciones existentes
from app.models.tipo_evento import TipoEvento
from app.models.usuario import Usuario
from app.models.evento import Evento

# NUEVOS MODELOS (Asegúrate de que los archivos existan en /models)
from app.models.tipo_qr import TipoQr 
from app.models.qr_code import QrCode
from app.models.qr_uso_log import QrUsoLog

# ... cualquier otro modelo adicional