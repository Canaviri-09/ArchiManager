import os
from flask import render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.documentos import documentos_bp
from app.extensions import db
from app.models_all import Archivo, Proyecto, EquipoProyecto
from app.utilidades import registrar_auditoria
from datetime import datetime

def verificar_acceso_proyecto(proyecto_id):
    """Valida si el usuario actual tiene acceso al proyecto según su rol."""
    if current_user.rol.nombre == "Administrador":
        return True
    if current_user.rol.nombre == "Arquitecto Manager":
        proyecto = Proyecto.query.filter_by(id=proyecto_id, responsable_id=current_user.id).first()
        return proyecto is not None
    # Colaborador Técnico
    pertenece = EquipoProyecto.query.filter_by(proyecto_id=proyecto_id, usuario_id=current_user.id).first()
    return pertenece is not None

@documentos_bp.route("/documentos")
@documentos_bp.route("/documentos/<int:proyecto_id>", endpoint="ver_documentos")
@documentos_bp.route("/documentacion/<int:proyecto_id>", endpoint="ver_documentacion")
@login_required
def index(proyecto_id=None):
    if proyecto_id is None:
        proyecto_id = request.args.get("proyecto_id", type=int)
    
    if current_user.rol.nombre == "Administrador":
        proyectos = Proyecto.query.all()
    elif current_user.rol.nombre == "Arquitecto Manager":
        proyectos = Proyecto.query.filter_by(responsable_id=current_user.id).all()
    else:
        proyectos = Proyecto.query.join(EquipoProyecto).filter(EquipoProyecto.usuario_id == current_user.id).all()
        
    documentos = []
    proyecto_seleccionado = None
    
    if proyecto_id:
        if verificar_acceso_proyecto(proyecto_id):
            proyecto_seleccionado = Proyecto.query.get(proyecto_id)
            documentos = Archivo.query.filter_by(proyecto_id=proyecto_id, eliminado=False).all()
        else:
            flash("No tienes autorización para consultar la documentación de este proyecto.", "danger")
            return redirect(url_for("documentos.index"))
            
    return render_template("documentos/index.html", proyectos=proyectos, documentos=documentos, proyecto_seleccionado=proyecto_seleccionado)

@documentos_bp.route("/documentos/subir/<int:proyecto_id>", methods=["POST"])
@login_required
def subir(proyecto_id):
    if not verificar_acceso_proyecto(proyecto_id):
        flash("No posees los permisos necesarios para añadir archivos aquí.", "danger")
        return redirect(url_for("documentos.index"))
        
    file = request.files.get("archivo_tecnico")
    tipo_archivo = request.form.get("tipo_archivo")
    
    if not file or file.filename == '':
        flash("Selecciona un archivo válido para procesar.", "warning")
        return redirect(url_for("documentos.index", proyecto_id=proyecto_id))
        
    filename_original = secure_filename(file.filename)
    
    documentos_existentes = Archivo.query.filter_by(proyecto_id=proyecto_id, nombre=filename_original).all()
    
    version_calculada = 1
    if documentos_existentes:
        version_calculada = len(documentos_existentes) + 1
        
    nombre_base, ext = os.path.splitext(filename_original)
    filename_servidor = f"PRY_{proyecto_id}_{nombre_base}_v{version_calculada}{ext}"
    
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'documentos')
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, filename_servidor)
    file.save(file_path)
    
    nuevo_archivo = Archivo(
        proyecto_id=proyecto_id,
        usuario_id=current_user.id,
        nombre=filename_original,
        tipo=tipo_archivo,
        url=f"uploads/documentos/{filename_servidor}",
        version_actual=version_calculada,
        eliminado=False
    )
    
    db.session.add(nuevo_archivo)
    db.session.commit()
    
    registrar_auditoria(f"SUBIÓ DOCUMENTO v{version_calculada}", "archivos", nuevo_archivo.id)
    flash(f"Archivo subido exitosamente como Versión {version_calculada}.", "success")
    return redirect(url_for("documentos.index", proyecto_id=proyecto_id))

@documentos_bp.route("/documentos/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar(id):
    archivo = Archivo.query.get_or_404(id)
    
    es_propietario = (archivo.usuario_id == current_user.id)
    es_superior = (current_user.rol.nombre in ["Administrador", "Arquitecto Manager"])
    
    if not (es_propietario or es_superior):
        flash("No cuenta con autorización para remover este documento técnico.", "danger")
        return redirect(url_for("documentos.index", proyecto_id=archivo.proyecto_id))
        
    archivo.eliminado = True
    db.session.commit()
    
    registrar_auditoria("ELIMINACIÓN LÓGICA DE DOCUMENTO", "archivos", archivo.id)
    flash("El documento ha sido removido del proyecto correctamente.", "info")
    return redirect(url_for("documentos.index", proyecto_id=archivo.proyecto_id))