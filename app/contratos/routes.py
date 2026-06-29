from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.contratos import contratos_bp
from app.extensions import db
from app.models_all import Contrato, Proyecto, TipoContrato
from app.utilidades import registrar_auditoria
from app.storage import subir_archivo, eliminar_archivo, extension_valida
from datetime import datetime


def permitir_escritura():
    return current_user.rol.nombre in ["Administrador", "Arquitecto Manager"]


@contratos_bp.route("/contratos", methods=["GET"])
@login_required
def index():
    rol = current_user.rol.nombre
    if rol == "Administrador":
        contratos = Contrato.query.all()
    elif rol == "Arquitecto Manager":
        contratos = Contrato.query.join(Proyecto).filter(
            Proyecto.responsable_id == current_user.id
        ).all()
    else:
        from app.models_all import EquipoProyecto
        contratos = Contrato.query.join(Proyecto).join(EquipoProyecto).filter(
            EquipoProyecto.usuario_id == current_user.id
        ).all()
    return render_template("contratos/index.html", contratos=contratos)


@contratos_bp.route("/contratos/crear", methods=["GET", "POST"])
@login_required
def crear():
    if not permitir_escritura():
        flash("No tienes permisos para registrar contratos.", "danger")
        return redirect(url_for("contratos.index"))

    if request.method == "POST":
        proyecto_id     = request.form.get("proyecto_id")
        tipo_contrato_id = request.form.get("tipo_contrato_id")
        numero_contrato = request.form.get("numero_contrato")
        fecha_firma_str = request.form.get("fecha_firma")
        estado          = request.form.get("estado")

        file = request.files.get("archivo_pdf")

        if not file or file.filename == "":
            flash("El documento PDF del contrato es obligatorio.", "danger")
            return redirect(request.url)

        # Validar que sea PDF
        if not extension_valida(file.filename, {"pdf"}):
            flash("Formato de archivo inválido. Solo se admiten documentos PDF.", "danger")
            return redirect(request.url)

        # Subir a Supabase Storage (carpeta: contratos/)
        url = subir_archivo(file, file.filename, carpeta="contratos")

        if not url:
            flash("Error al subir el PDF a la nube. Intenta de nuevo.", "danger")
            return redirect(request.url)

        fecha_firma = (
            datetime.strptime(fecha_firma_str, "%Y-%m-%d").date()
            if fecha_firma_str
            else None
        )

        nuevo_contrato = Contrato(
            proyecto_id=proyecto_id,
            tipo_contrato_id=tipo_contrato_id,
            numero_contrato=numero_contrato,
            fecha_firma=fecha_firma,
            archivo_pdf=url,            # URL pública de Supabase Storage
            estado=estado,
        )
        db.session.add(nuevo_contrato)
        db.session.commit()

        registrar_auditoria("REGISTRÓ CONTRATO", "contratos", nuevo_contrato.id)
        flash("Contrato legal cargado y asociado al proyecto con éxito.", "success")
        return redirect(url_for("contratos.index"))

    # GET — cargar selectores
    if current_user.rol.nombre == "Administrador":
        proyectos = Proyecto.query.all()
    else:
        proyectos = Proyecto.query.filter_by(responsable_id=current_user.id).all()

    tipos = TipoContrato.query.all()
    return render_template("contratos/crear.html", proyectos=proyectos, tipos=tipos)


@contratos_bp.route("/contratos/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar(id):
    if not permitir_escritura():
        flash("No tienes permisos para eliminar contratos.", "danger")
        return redirect(url_for("contratos.index"))

    contrato = Contrato.query.get_or_404(id)

    # Eliminar PDF del Storage antes de borrar el registro
    if contrato.archivo_pdf:
        eliminar_archivo(contrato.archivo_pdf)

    db.session.delete(contrato)
    db.session.commit()

    registrar_auditoria("ELIMINÓ CONTRATO", "contratos", id)
    flash("Contrato eliminado correctamente.", "success")
    return redirect(url_for("contratos.index"))
