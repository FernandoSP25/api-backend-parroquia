from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from uuid import UUID
from typing import List

from app.models.asistencia import Asistencia
from app.models.evento import Evento
from app.schemas.asistencia import AsistenciaUpdate
from app.models.usuario import Usuario
from app.models.confirmante import Confirmante
from app.models.catequista import Catequista
from sqlalchemy.orm import joinedload   
from app.models.catequista_grupo import CatequistaGrupo
from app.models.usuario_rol import UsuarioRol
from app.models.grupo import Grupo

class AsistenciaService:

    @staticmethod
    def obtener_por_evento(db: Session, evento_id: UUID):
        """Devuelve la lista de asistencias de un evento específico"""
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(status_code=404, detail="El evento no existe.")
        
        return db.query(Asistencia).filter(Asistencia.evento_id == evento_id).all()

    @staticmethod
    def registrar_asistencia_masiva(db: Session, evento_id: UUID, catequista_id: UUID, asistencias_data: List[AsistenciaUpdate], ip_address: str = None):
        """El catequista envía toda la lista del aula y se guarda/actualiza de golpe"""
        
        # 1. Validar evento
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(status_code=404, detail="El evento no existe.")

        asistencias_actualizadas = []
        
        for data in asistencias_data:
            # Buscamos si el registro ya existe para este alumno en este evento
            asistencia = db.query(Asistencia).filter(
                Asistencia.evento_id == evento_id,
                Asistencia.usuario_id == data.usuario_id
            ).first()

            if asistencia:
                # Si existe, la actualizamos (ej. le cambia de Falta a Tarde)
                asistencia.estado_id = data.estado_id
                asistencia.observaciones = data.observaciones
                asistencia.registrada_por = catequista_id
                asistencia.fecha = datetime.utcnow()
                asistencia.ip_address = ip_address
            else:
                # Si no existía, la creamos
                asistencia = Asistencia(
                    usuario_id=data.usuario_id,
                    evento_id=evento_id,
                    estado_id=data.estado_id,
                    observaciones=data.observaciones,
                    registrada_por=catequista_id,
                    ip_address=ip_address
                )
                db.add(asistencia)
            
            asistencias_actualizadas.append(asistencia)
        
        try:
            db.commit()
            # Opcional: refrescar la lista si necesitas devolver los datos exactos
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error de base de datos al guardar la asistencia.")

        return asistencias_actualizadas
    
    
    @staticmethod
    def obtener_checklist_evento(db: Session, evento_id: UUID, current_user: Usuario):
        """Genera la lista de alumnos para tomar asistencia, filtrando por el rol del usuario"""
        
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(status_code=404, detail="El evento no existe.")

        # 1. Determinar si el usuario es ADMIN
        es_admin = any(ur.rol.nombre == "ADMIN" for ur in current_user.roles if ur.activo)

        # 2. Iniciar la consulta base de Confirmantes Activos
        query = db.query(Confirmante).options(
            joinedload(Confirmante.usuario),
            joinedload(Confirmante.grupo)
        ).filter(Confirmante.activo == True)

        # 3. Lógica de Filtros de Seguridad (Admin vs Catequista)
        if evento.grupo_id:
            # A) Es un evento de un GRUPO ESPECÍFICO (ej. Clase Grupo Mateo)
            query = query.filter(Confirmante.grupo_id == evento.grupo_id)
            
            if not es_admin:
                # Si es catequista, verificar que esté asignado a ese grupo
                tiene_permiso = db.query(CatequistaGrupo).join(Catequista).filter(
                    Catequista.usuario_id == current_user.id,
                    CatequistaGrupo.grupo_id == evento.grupo_id,
                    CatequistaGrupo.activo == True
                ).first()
                if not tiene_permiso:
                    raise HTTPException(status_code=403, detail="No tienes permisos sobre el grupo de este evento.")
        else:
            # B) Es un evento GENERAL (ej. Misa de toda la parroquia)
            if not es_admin:
                # El catequista solo debe ver a los confirmantes de SUS grupos
                grupos_del_catequista = db.query(CatequistaGrupo.grupo_id).join(Catequista).filter(
                    Catequista.usuario_id == current_user.id,
                    CatequistaGrupo.activo == True
                ).subquery()
                
                query = query.filter(Confirmante.grupo_id.in_(grupos_del_catequista))

        # Ordenar alfabéticamente por apellidos
        query = query.join(Usuario, Confirmante.usuario_id == Usuario.id).order_by(Usuario.apellidos.asc())
        confirmantes = query.all()

        # 4. Obtener las asistencias ya registradas (por si está editando)
        asistencias_registradas = {
            a.usuario_id: a 
            for a in db.query(Asistencia).filter(Asistencia.evento_id == evento_id).all()
        }

        # 5. Construir la respuesta final cruzando Confirmantes con Asistencias
        checklist = []
        for conf in confirmantes:
            asistencia_previa = asistencias_registradas.get(conf.usuario_id)
            
            checklist.append({
                "confirmante_id": conf.id,
                "usuario_id": conf.usuario_id,
                "nombres": conf.usuario.nombres,
                "apellidos": conf.usuario.apellidos,
                "foto_url": conf.usuario.foto_url,
                "grupo_nombre": conf.grupo.nombre if conf.grupo else "Sin Grupo",
                # MAGIA AQUÍ: Si ya le tomaron lista, pone su estado. Si no, pone 3 (Falta por defecto)
                "estado_id": asistencia_previa.estado_id if asistencia_previa else 3,
                "observaciones": asistencia_previa.observaciones if asistencia_previa else None
            })

        return checklist

    @staticmethod
    def obtener_matriz_por_tipo(db: Session, tipo_evento_id: int, modo: str = "confirmantes"):
        """
        Genera la matriz de asistencias usando 100% ORM SQLAlchemy.
        Devuelve exactamente la estructura que el Frontend (React) necesita.
        """
        from datetime import date
        
        # 1. Traer COLUMNAS: Eventos de este tipo (pasados y de hoy)
        eventos = db.query(Evento).filter(
            Evento.tipo_id == tipo_evento_id,
            Evento.activo == True,
            Evento.fecha <= date.today()
        ).order_by(Evento.fecha.asc(), Evento.hora_inicio.asc()).all()

        if not eventos:
            return {"eventos": [], "personas": [], "asistencias": []}

        evento_ids = [e.id for e in eventos]

        # 2. Traer FILAS: Personas (Confirmantes o Catequistas)
        personas_data = []
        if modo == "confirmantes":
            confirmantes = db.query(Confirmante).options(
                joinedload(Confirmante.usuario),
                joinedload(Confirmante.grupo)
            ).filter(Confirmante.activo == True).all()
            
            # Ordenar por apellido usando Python
            confirmantes.sort(key=lambda c: c.usuario.apellidos or "")
            
            for c in confirmantes:
                personas_data.append({
                    "id": str(c.usuario_id), # Usamos usuario_id para cruzar con Asistencia
                    "nombres": c.usuario.nombres,
                    "apellidos": c.usuario.apellidos,
                    "etiqueta": c.grupo.nombre if c.grupo else "Sin asignar"
                })
                
        elif modo == "catequistas":
            # Traemos a los catequistas con sus usuarios
            catequistas = db.query(Catequista).options(
                joinedload(Catequista.usuario)
            ).filter(Catequista.activo == True).all()
            
            catequistas.sort(key=lambda c: c.usuario.apellidos or "")
            
            for cat in catequistas:
                # Buscamos su grupo principal (opcional)
                grupo_rel = db.query(CatequistaGrupo).options(joinedload(CatequistaGrupo.grupo)).filter(
                    CatequistaGrupo.catequista_id == cat.id, 
                    CatequistaGrupo.activo == True
                ).first()
                
                personas_data.append({
                    "id": str(cat.usuario_id),
                    "nombres": cat.usuario.nombres,
                    "apellidos": cat.usuario.apellidos,
                    "etiqueta": grupo_rel.grupo.nombre if grupo_rel and grupo_rel.grupo else "Catequista"
                })

        # 3. Traer INTERSECCIONES: Las asistencias registradas
        # Solo traemos las asistencias de los eventos que encontramos
        asistencias_db = db.query(Asistencia).filter(
            Asistencia.evento_id.in_(evento_ids)
        ).all()

        # Diccionario traductor de IDs a Textos para el Frontend
        mapa_estados = {
            1: "PRESENTE",
            2: "FALTA",
            3: "TARDANZA",
            4: "FALTA_JUSTIFICADA"
        }

        asistencias_data = []
        for a in asistencias_db:
            asistencias_data.append({
                "personaId": str(a.usuario_id),
                "eventoId": str(a.evento_id),
                "estado": mapa_estados.get(a.estado_id, "FALTA") 
            })

        # 4. Empaquetar y enviar al Frontend
        return {
            "eventos": [
                {
                    "id": str(e.id), 
                    "fecha": e.fecha.strftime("%d/%m"), 
                    "nombre": e.nombre
                } for e in eventos
            ],
            "personas": personas_data,
            "asistencias": asistencias_data
        }