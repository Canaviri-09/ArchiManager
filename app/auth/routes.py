from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import bcrypt
from app.auth import auth_bp
from app.models_all import Usuario
from app.utilidades import registrar_auditoria


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Si ya hay sesión activa, se evita mostrar el login de nuevo
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        correo = request.form.get("correo")
        password = request.form.get("password")

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and not usuario.activo:
            flash("Tu cuenta está desactivada. Contacta al Administrador.", "warning")
            return render_template("auth/login.html")

        if usuario and bcrypt.check_password_hash(usuario.password, password):
            login_user(usuario)
            registrar_auditoria("INICIÓ SESIÓN", "usuarios", usuario.id)
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("dashboard.index"))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    registrar_auditoria("CERRÓ SESIÓN", "usuarios", current_user.id)
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))
