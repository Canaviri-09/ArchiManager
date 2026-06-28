from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db, bcrypt
from app.usuarios import usuarios_bp
from app.models_all import Usuario, Rol, Especialidad
from app.utilidades import role_required, registrar_auditoria


@usuarios_bp.route("/")
@login_required
@role_required("Administrador")
def listar():
    # Filtros opcionales por rol y especialidad (Módulo 2 del plan)
    rol_id = request.args.get("rol_id", type=int)
    especialidad_id = request.args.get("especialidad_id", type=int)

    consulta = Usuario.query

    if rol_id:
        consulta = consulta.filter(Usuario.rol_id == rol_id)
    if especialidad_id:
        consulta = consulta.filter(Usuario.especialidad_id == especialidad_id)

    usuarios = consulta.order_by(Usuario.nombre).all()
    roles = Rol.query.order_by(Rol.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()

    return render_template(
        "usuarios/listar.html",
        usuarios=usuarios,
        roles=roles,
        especialidades=especialidades,
        rol_id_seleccionado=rol_id,
        especialidad_id_seleccionada=especialidad_id,
    )


@usuarios_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
@role_required("Administrador")
def crear():
    roles = Rol.query.order_by(Rol.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        rol_id = request.form.get("rol_id", type=int)
        especialidad_id = request.form.get("especialidad_id", type=int) or None
        activo = request.form.get("activo") == "on"

        if not nombre or not correo or not password or not rol_id:
            flash("Nombre, correo, contraseña y rol son obligatorios.", "danger")
            return render_template("usuarios/nuevo.html", roles=roles, especialidades=especialidades)

        if Usuario.query.filter_by(correo=correo).first():
            flash("Ya existe un usuario registrado con ese correo.", "danger")
            return render_template("usuarios/nuevo.html", roles=roles, especialidades=especialidades)

        hashed = bcrypt.generate_password_hash(password).decode("utf-8")
        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=hashed,
            rol_id=rol_id,
            especialidad_id=especialidad_id,
            activo=activo,
        )
        db.session.add(usuario)
        db.session.commit()

        registrar_auditoria("CREÓ", "usuarios", usuario.id)
        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/nuevo.html", roles=roles, especialidades=especialidades)


@usuarios_bp.route("/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
@role_required("Administrador")
def editar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    roles = Rol.query.order_by(Rol.nombre).all()
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        nueva_password = request.form.get("password", "")
        rol_id = request.form.get("rol_id", type=int)
        especialidad_id = request.form.get("especialidad_id", type=int) or None
        activo = request.form.get("activo") == "on"

        if not nombre or not correo or not rol_id:
            flash("Nombre, correo y rol son obligatorios.", "danger")
            return render_template("usuarios/editar.html", usuario=usuario, roles=roles, especialidades=especialidades)

        correo_existente = Usuario.query.filter(Usuario.correo == correo, Usuario.id != usuario.id).first()
        if correo_existente:
            flash("Ese correo ya está en uso por otro usuario.", "danger")
            return render_template("usuarios/editar.html", usuario=usuario, roles=roles, especialidades=especialidades)

        # Evitar que el Administrador se desactive a sí mismo por accidente
        if usuario.id == current_user.id and not activo:
            flash("No puedes desactivar tu propio usuario.", "warning")
            return render_template("usuarios/editar.html", usuario=usuario, roles=roles, especialidades=especialidades)

        usuario.nombre = nombre
        usuario.correo = correo
        usuario.rol_id = rol_id
        usuario.especialidad_id = especialidad_id
        usuario.activo = activo

        if nueva_password:
            usuario.password = bcrypt.generate_password_hash(nueva_password).decode("utf-8")

        db.session.commit()
        registrar_auditoria("MODIFICÓ", "usuarios", usuario.id)
        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("usuarios.listar"))

    return render_template("usuarios/editar.html", usuario=usuario, roles=roles, especialidades=especialidades)


@usuarios_bp.route("/<int:usuario_id>/eliminar", methods=["POST"])
@login_required
@role_required("Administrador")
def eliminar(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if usuario.id == current_user.id:
        flash("No puedes eliminar tu propio usuario.", "warning")
        return redirect(url_for("usuarios.listar"))

    db.session.delete(usuario)
    db.session.commit()
    registrar_auditoria("ELIMINÓ", "usuarios", usuario_id)
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("usuarios.listar"))
