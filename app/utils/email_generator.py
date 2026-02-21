import unicodedata
import re
from datetime import date

def limpiar_texto(texto: str) -> str:
    """
    Convierte a minúsculas, quita tildes, ñ -> n y elimina caracteres especiales.
    Ej: "María-José" -> "mariajose"
    """
    if not texto:
        return ""
    
    # 1. Normalizar unicode (separa letras de tildes: 'á' se vuelve 'a' + '´')
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    
    # 2. Quedarse solo con caracteres ASCII (elimina las tildes separadas)
    texto_ascii = texto_normalizado.encode('ASCII', 'ignore').decode('utf-8')
    
    # 3. Pasar a minúsculas y borrar todo lo que no sea letra (a-z)
    return re.sub(r'[^a-z]', '', texto_ascii.lower())

def generar_email_institucional(nombres: str, apellidos: str, fecha_nacimiento: date) -> str:
    """
    Genera un email único basado en el nombre y fecha.
    Formato: [primer_nombre][2_letras_ape1][2_letras_ape2][DDMM]@parroquiasjmv.com
    
    Ejemplo: 
    - Juan Perez Gonzales (12/02) -> juanpego1202@parroquiasjmv.com
    - Luis Vega (05/11) -> luisve0511@parroquiasjmv.com
    """
    
    # 1. Validaciones básicas
    if not nombres or not apellidos or not fecha_nacimiento:
        return ""

    # 2. Procesar Nombre (Tomamos solo el primero)
    partes_nombre = nombres.strip().split()
    nombre_base = limpiar_texto(partes_nombre[0]) if partes_nombre else "usuario"

    # 3. Procesar Apellidos
    partes_apellido = apellidos.strip().split()
    
    # Apellido 1: Primeras 2 letras
    ape1 = ""
    if len(partes_apellido) > 0:
        ape1 = limpiar_texto(partes_apellido[0])[:2]
    
    # Apellido 2: Primeras 2 letras (Si existe)
    ape2 = ""
    if len(partes_apellido) > 1:
        ape2 = limpiar_texto(partes_apellido[1])[:2]

    # 4. Procesar Fecha (DDMM)
    dia = f"{fecha_nacimiento.day:02d}"
    mes = f"{fecha_nacimiento.month:02d}"

    # 5. Unir
    email_user = f"{nombre_base}{ape1}{ape2}{dia}{mes}"
    
    return f"{email_user}@parroquiasjmv.com"


def generar_email_staff(nombres: str, apellidos: str) -> str:
    """
    Genera un email formato corporativo: nombre.apellido@parroquiasjmv.com
    Usado para Catequistas y Admins.
    """
    if not nombres or not apellidos:
        return ""

    # Tomar primer nombre y primer apellido
    nombre_base = limpiar_texto(nombres.split()[0])
    apellido_base = limpiar_texto(apellidos.split()[0])

    return f"{nombre_base}.{apellido_base}@parroquiasjmv.com"