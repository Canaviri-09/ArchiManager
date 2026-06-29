from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.documentos import documentos_bp
from app.extensions import db
from app.models_all import Archivo, Proyecto, EquipoProyecto
from app.utilidades import registrar_auditoria
from app.storage import subir_archivo, eliminar_archivo, extension_valida
from datetime import datetime

# Extensiones permitidas por categoría
EXT_IMAGEN    = {"jpg", "jpeg", "png", "webp"}
EXT_DOCUMENTO = {"pdf"}
EXT_VIDEO     = {"mp4"}
EXT_TODAS     = EXT_IMAGEN | EXT_DOCUMENTO | EXT_VIDEO


def _tipo_archivo(nombre):
    """Determina el tipo según la extensión."""
    ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    if ext in EXT_IMAGEN:
        return "imagen"
    if ext in EXT_DOCUMENTO:
        return "documento"
    if ext in EXT_VIDEO:
        return "video"
    return "otro"


def verificar_acceso_proyecto(proyecto_id):
    """Valida si el usuario actual tiene acceso al proyecto según su rol."""
    if current_user.rol.nombre == "Administrador":
        return True
    if current_user.rol.nombre == "Arquitecto Manager":
        proyecto = Proyecto.query.filter_by(id=proyecto_id, responsable_id=current_user.id).first()
        return proyecto is not None
    # Colaborador Técnico
    pertenece = EquipoProyecto.query.filter_by(
        proyecto_id=proyecto_id, usuario_id=current_user.id
    ).first()
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
        proyectos = Proyecto.query.join(EquipoProyecto).filter(
            EquipoProyecto.usuario_id == current_user.id
        ).all()

    documentos = []
    proyecto_seleccionado = None

    if proyecto_id:
        if verificar_acceso_proyecto(proyecto_id):
            proyecto_seleccionado = Proyecto.query.get(proyecto_id)
            documentos = Archivo.query.filter_by(
                proyecto_id=proyecto_id, eliminado=False
            ).all()
        else:
            flash("No tienes autorización para consultar la documentación de este proyecto.", "danger")
            return redirect(url_for("documentos.index"))

    return render_template(
        "documentos/index.html",
        proyectos=proyectos,
        documentos=documentos,
        proyecto_seleccionado=proyecto_seleccionado,
    )


@documentos_bp.route("/documentos/subir/<int:proyecto_id>", methods=["POST"])
@login_required
def subir(proyecto_id):
    if not verificar_acceso_proyecto(proyecto_id):
        flash("No posees los permisos necesarios para añadir archivos aquí.", "danger")
        return redirect(url_for("documentos.index"))

    file = request.files.get("archivo_tecnico")
    tipo_archivo = request.form.get("tipo_archivo")

    if not file or file.filename == "":
        flash("Selecciona un archivo válido para procesar.", "warning")
        return redirect(url_for("documentos.index", proyecto_id=proyecto_id))

    # Validar extensión
    if not extension_valida(file.filename, EXT_TODAS):
        flash("Tipo de archivo no permitido. Solo JPG, PNG, WEBP, PDF y MP4.", "danger")
        return redirect(url_for("documentos.index", proyecto_id=proyecto_id))

    nombre_original = file.filename

    # Calcular versión
    documentos_existentes = Archivo.query.filter_by(
        proyecto_id=proyecto_id, nombre=nombre_original
    ).all()
    version_calculada = len(documentos_existentes) + 1

    # Subir a Supabase Storage (carpeta: documentos/<proyecto_id>/)
    url = subir_archivo(file, nombre_original, carpeta=f"documentos/{proyecto_id}")

    if not url:
        flash("Error al subir el archivo a la nube. Intenta de nuevo.", "danger")
        return redirect(url_for("documentos.index", proyecto_id=proyecto_id))

    # Determinar tipo si no viene del formulario
    if not tipo_archivo:
        tipo_archivo = _tipo_archivo(nombre_original)

    nuevo_archivo = Archivo(
        proyecto_id=proyecto_id,
        usuario_id=current_user.id,
        nombre=nombre_original,
        tipo=tipo_archivo,
        url=url,                        # URL pública de Supabase Storage
        version_actual=version_calculada,
        eliminado=False,
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

    es_propietario = archivo.usuario_id == current_user.id
    es_superior = current_user.rol.nombre in ["Administrador", "Arquitecto Manager"]

    if not (es_propietario or es_superior):
        flash("No cuenta con autorización para remover este documento técnico.", "danger")
        return redirect(url_for("documentos.index", proyecto_id=archivo.proyecto_id))

    # Borrado lógico (el archivo permanece en Storage)
    archivo.eliminado = True
    db.session.commit()

    registrar_auditoria("ELIMINACIÓN LÓGICA DE DOCUMENTO", "archivos", archivo.id)
    flash("El documento ha sido removido del proyecto correctamente.", "info")
    return redirect(url_for("documentos.index", proyecto_id=archivo.proyecto_id))
