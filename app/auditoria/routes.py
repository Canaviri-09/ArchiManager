from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.auditoria import auditoria_bp
from app.models_all import Auditoria

@auditoria_bp.route("/auditoria", methods=["GET"])
@login_required
def index():
    # REGLA DE SEGURIDAD MÁXIMA: Acceso exclusivo para el Administrador
    if current_user.rol.nombre != "Administrador":
        flash("Acceso denegado. No tienes los permisos requerimiento para ver la bitácora de auditoría global.", "danger")
        return redirect(url_for("dashboard.index"))
        
    # Obtener todas las auditorías ordenadas cronológicamente (las más recientes primero)
    bitacora = Auditoria.query.order_by(Auditoria.fecha.desc()).all()
    
    return render_template("auditoria/index.html", bitacora=bitacora)