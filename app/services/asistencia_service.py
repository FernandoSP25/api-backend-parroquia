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
from datetime import date

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
        """Genera la lista de personas para tomar asistencia, respetando el público objetivo (dirigido_a) y filtros de seguridad"""
        
        evento = db.query(Evento).filter(Evento.id == evento_id).first()
        if not evento:
            raise HTTPException(status_code=404, detail="El evento no existe.")

        # 1. Determinar si el usuario es ADMIN
        es_admin = any(ur.rol.nombre == "ADMIN" for ur in current_user.roles if ur.activo)

        # 2. Obtener las asistencias ya registradas (por si está editando)
        asistencias_registradas = {
            a.usuario_id: a 
            for a in db.query(Asistencia).filter(Asistencia.evento_id == evento_id).all()
        }

        checklist = []

        # =================================================================
        # BLOQUE 1: LÓGICA PARA CONFIRMANTES (Si el evento es para ellos o para TODOS)
        # =================================================================
        if evento.dirigido_a in ["CONFIRMANTES", "TODOS"]:
            query_conf = db.query(Confirmante).options(
                joinedload(Confirmante.usuario),
                joinedload(Confirmante.grupo)
            ).filter(Confirmante.activo == True)

            # --- Filtros de Seguridad ---
            if evento.grupo_id:
                query_conf = query_conf.filter(Confirmante.grupo_id == evento.grupo_id)
                
                if not es_admin:
                    tiene_permiso = db.query(CatequistaGrupo).join(Catequista).filter(
                        Catequista.usuario_id == current_user.id,
                        CatequistaGrupo.grupo_id == evento.grupo_id,
                        CatequistaGrupo.activo == True
                    ).first()
                    if not tiene_permiso:
                        raise HTTPException(status_code=403, detail="No tienes permisos sobre el grupo de este evento.")
            else:
                if not es_admin:
                    grupos_del_catequista = db.query(CatequistaGrupo.grupo_id).join(Catequista).filter(
                        Catequista.usuario_id == current_user.id,
                        CatequistaGrupo.activo == True
                    ).subquery()
                    query_conf = query_conf.filter(Confirmante.grupo_id.in_(grupos_del_catequista))

            # Ejecutamos consulta de Confirmantes
            confirmantes = query_conf.all()

            for conf in confirmantes:
                asistencia_previa = asistencias_registradas.get(conf.usuario_id)
                checklist.append({
                    "confirmante_id": str(conf.id), # Mantenemos esta llave para que tu Frontend React no se rompa
                    "usuario_id": str(conf.usuario_id),
                    "nombres": conf.usuario.nombres,
                    "apellidos": conf.usuario.apellidos,
                    "foto_url": conf.usuario.foto_url,
                    "grupo_nombre": conf.grupo.nombre if conf.grupo else "Sin Grupo",
                    "rol_persona": "CONFIRMANTE",
                    "estado_id": asistencia_previa.estado_id if asistencia_previa else 3,
                    "observaciones": asistencia_previa.observaciones if asistencia_previa else None
                })
        
        # =================================================================
        # BLOQUE 2: LÓGICA PARA CATEQUISTAS (Si el evento es para ellos o para TODOS)
        # =================================================================
        if evento.dirigido_a in ["CATEQUISTAS", "TODOS"]:
            query_cat = db.query(Catequista).options(
                joinedload(Catequista.usuario)
            ).filter(Catequista.activo == True)

            # Si el evento es de un grupo específico, cruzamos con CatequistaGrupo
            if evento.grupo_id:
                query_cat = query_cat.join(CatequistaGrupo).filter(
                    CatequistaGrupo.grupo_id == evento.grupo_id, 
                    CatequistaGrupo.activo == True
                )
            
            catequistas = query_cat.all()

            # --- MAGIA: Buscar los nombres de los grupos de estos catequistas ---
            # Creamos un diccionario rápido para no hacer consultas lentas dentro del for
            dict_grupos_cats = {}
            if catequistas and not evento.grupo_id:
                cat_ids = [cat.id for cat in catequistas]
                from app.models.grupo import Grupo # Asegúrate de importar el modelo
                
                # Buscamos a qué grupo pertenece cada catequista activo
                relaciones = db.query(CatequistaGrupo.catequista_id, Grupo.nombre).join(
                    Grupo, CatequistaGrupo.grupo_id == Grupo.id
                ).filter(
                    CatequistaGrupo.catequista_id.in_(cat_ids),
                    CatequistaGrupo.activo == True
                ).all()
                
                for rel in relaciones:
                    dict_grupos_cats[rel.catequista_id] = rel.nombre

            for cat in catequistas:
                asistencia_previa = asistencias_registradas.get(cat.usuario_id)
                
                # Si el evento es de un grupo específico, usamos ese nombre. 
                # Si es general, lo sacamos de nuestro diccionario.
                if evento.grupo_id and evento.grupo:
                    nombre_grupo = evento.grupo.nombre
                else:
                    nombre_grupo = dict_grupos_cats.get(cat.id, "Sin Grupo")

                checklist.append({
                    "confirmante_id": str(cat.id), 
                    "usuario_id": str(cat.usuario_id),
                    "nombres": cat.usuario.nombres,
                    "apellidos": cat.usuario.apellidos,
                    "foto_url": cat.usuario.foto_url,
                    "grupo_nombre": nombre_grupo ,
                    "rol_persona": "CATEQUISTA",
                    "estado_id": asistencia_previa.estado_id if asistencia_previa else 3,
                    "observaciones": asistencia_previa.observaciones if asistencia_previa else None
                })

        # =================================================================
        # BLOQUE 3: ORDENAR Y RETORNAR
        # =================================================================
        # Ordenamos toda la lista combinada alfabéticamente por apellidos
        checklist_ordenado = sorted(checklist, key=lambda x: x["apellidos"] or "")

        return checklist_ordenado

    @staticmethod
    def obtener_matriz_por_tipo(db: Session, tipo_evento_id: int, modo: str = "confirmantes", grupo_id_filtro: UUID = None):
        from datetime import date
        filtro_dirigido = ["CONFIRMANTES", "TODOS"] if modo == "confirmantes" else ["CATEQUISTAS", "TODOS"]
        
        # ==========================================
        # 1. Traer COLUMNAS (Eventos)
        # ==========================================
        # 👇 CORRECCIÓN 1: Se llama 'query_eventos' y NO tiene .all() todavía
        query_eventos = db.query(Evento).filter(
            Evento.tipo_id == tipo_evento_id,
            Evento.activo == True,
            #Evento.fecha <= date.today(),
            Evento.dirigido_a.in_(filtro_dirigido)
        )

        # Si hay filtro de grupo, le agregamos la condición a la consulta "abierta"
        if grupo_id_filtro:
            from sqlalchemy import or_
            query_eventos = query_eventos.filter(
                or_(Evento.grupo_id == None, Evento.grupo_id == grupo_id_filtro)
            )

        # 👇 Ahora sí, ordenamos y ejecutamos la consulta final
        eventos = query_eventos.order_by(Evento.fecha.asc(), Evento.hora_inicio.asc()).all()

        if not eventos:
            return {"eventos": [], "personas": [], "asistencias": []}

        evento_ids = [e.id for e in eventos]

        # ==========================================
        # 2. Traer FILAS (Personas)
        # ==========================================
        personas_data = []
        if modo == "confirmantes":
            # 👇 CORRECCIÓN 2: Se llama 'query_conf' y NO tiene .all() todavía
            query_conf = db.query(Confirmante).options(
                joinedload(Confirmante.usuario),
                joinedload(Confirmante.grupo)
            ).filter(Confirmante.activo == True)
            
            if grupo_id_filtro:
                query_conf = query_conf.filter(Confirmante.grupo_id == grupo_id_filtro)
                
            # 👇 Ejecutamos la consulta final
            confirmantes = query_conf.all()
            
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

        # ==========================================
        # 3. Traer INTERSECCIONES (Asistencias)
        # ==========================================
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

        # ==========================================
        # 4. Empaquetar y enviar al Frontend
        # ==========================================
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