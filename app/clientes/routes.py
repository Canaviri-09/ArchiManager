from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.clientes import clientes_bp
from app.extensions import db
from app.models_all import Cliente
from app.utilidades import registrar_auditoria

def admin_o_manager_requerido():
    # Helper para restringir acceso de escritura a Colaboradores Técnicos
    return current_user.rol.nombre in ["Administrador", "Arquitecto Manager"]

@clientes_bp.route("/clientes", methods=["GET"])
@login_required
def index():
    # Búsqueda en tiempo real o por formulario
    busqueda = request.args.get("buscar", "").strip()
    if busqueda:
        clientes = Cliente.query.filter(
            (Cliente.nombre.ilike(f"%{busqueda}%")) | 
            (Cliente.empresa.ilike(f"%{busqueda}%")) |
            (Cliente.nit.ilike(f"%{busqueda}%"))
        ).all()
    else:
        clientes = Cliente.query.all()
    return render_template("clientes/index.html", clientes=clientes, buscar=busqueda)

@clientes_bp.route("/clientes/crear", methods=["GET", "POST"])
@login_required
def crear():
    if not admin_o_manager_requerido():
        flash("No tienes permisos para realizar esta acción.", "danger")
        return redirect(url_for("clientes.index"))
        
    if request.method == "POST":
        nombre = request.form.get("nombre")
        empresa = request.form.get("empresa")
        telefono = request.form.get("telefono")
        correo = request.form.get("correo")
        nit = request.form.get("nit")
        
        nuevo_cliente = Cliente(
            nombre=nombre,
            empresa=empresa,
            telefono=telefono,
            correo=correo,
            nit=nit
        )
        db.session.add(nuevo_cliente)
        db.session.commit()
        
        registrar_auditoria("CREÓ CLIENTE", "clientes", nuevo_cliente.id)
        flash("Cliente registrado exitosamente.", "success")
        return redirect(url_for("clientes.index"))
        
    return render_template("clientes/crear.html")

@clientes_bp.route("/clientes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    if not admin_o_manager_requerido():
        flash("No tienes permisos para realizar esta acción.", "danger")
        return redirect(url_for("clientes.index"))
        
    # AQUÍ ESTÁ EL CAMBIO: Debe terminar en 404
    cliente = Cliente.query.get_or_404(id)
    
    if request.method == "POST":
        cliente.nombre = request.form.get("nombre")
        cliente.empresa = request.form.get("empresa")
        cliente.telefono = request.form.get("telefono")
        cliente.correo = request.form.get("correo")
        cliente.nit = request.form.get("nit")
        
        db.session.commit()
        registrar_auditoria("EDITÓ CLIENTE", "clientes", cliente.id)
        flash("Información del cliente actualizada.", "success")
        return redirect(url_for("clientes.index"))
        
    return render_template("clientes/editar.html", cliente=cliente)


@clientes_bp.route("/clientes/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar(id):
    if not admin_o_manager_requerido():
        flash("No tienes permisos para realizar esta acción.", "danger")
        return redirect(url_for("clientes.index"))
        
    cliente = Cliente.query.get_or_404(id)
    
    try:
        cliente_id = cliente.id
        
        db.session.delete(cliente)
        db.session.commit()
        
        registrar_auditoria("ELIMINÓ CLIENTE", "clientes", cliente_id)
        flash("Cliente eliminado exitosamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash("No se puede eliminar el cliente porque tiene proyectos vinculados.", "danger")
        
    return redirect(url_for("clientes.index"))

    