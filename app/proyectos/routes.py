from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.proyectos import proyectos_bp
from app.extensions import db
from app.models_all import Proyecto, Usuario, Cliente, EquipoProyecto, Ubicacion, Rol
from app.utilidades import registrar_auditoria
from datetime import datetime
from app.models_all import AvanceProyecto 

@proyectos_bp.route("/proyectos", methods=["GET"])
@login_required
def index():
    rol = current_user.rol.nombre
    
    if rol == "Administrador":
        proyectos = Proyecto.query.all()
    elif rol == "Arquitecto Manager":
        proyectos = Proyecto.query.filter_by(responsable_id=current_user.id).all()
    else:  # Colaborador Técnico
        proyectos = Proyecto.query.join(EquipoProyecto).filter(EquipoProyecto.usuario_id == current_user.id).all()
        
    return render_template("proyectos/index.html", proyectos=proyectos)

@proyectos_bp.route("/proyectos/crear", methods=["GET", "POST"])
@login_required
def crear():
    if current_user.rol.nombre == "Colaborador Técnico":
        flash("No tienes permisos para crear proyectos.", "danger")
        return redirect(url_for("proyectos.index"))
        
    if request.method == "POST":
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        descripcion = request.form.get("descripcion")
        presupuesto = request.form.get("presupuesto")
        estado = request.form.get("estado")
        cliente_id = request.form.get("cliente_id")
        responsable_id = request.form.get("responsable_id") if current_user.rol.nombre == "Administrador" else current_user.id
        
        nuevo_proyecto = Proyecto(
            codigo=codigo,
            nombre=nombre,
            descripcion=descripcion,
            presupuesto=presupuesto,
            estado=estado,
            cliente_id=cliente_id,
            responsable_id=responsable_id,
            avance_actual=0
        )
        db.session.add(nuevo_proyecto)
        db.session.flush() 
        
        nueva_ubicacion = Ubicacion(
            proyecto_id=nuevo_proyecto.id,
            pais=request.form.get("pais"),
            departamento=request.form.get("departamento"),
            municipio=request.form.get("municipio"),
            zona=request.form.get("zona"),
            calle=request.form.get("calle"),
            numero=request.form.get("numero"),
            latitud=float(request.form.get("latitud")) if request.form.get("latitud") else None,
            longitud=float(request.form.get("longitud")) if request.form.get("longitud") else None
        )
        db.session.add(nueva_ubicacion)
        db.session.commit()
        
        registrar_auditoria("CREÓ PROYECTO Y UBICACIÓN", "proyectos", nuevo_proyecto.id)
        flash("Proyecto y ubicación estratégica registrados correctamente.", "success")
        return redirect(url_for("proyectos.index"))
        
    clientes = Cliente.query.all()
    
    managers = Usuario.query.join(Rol, Usuario.rol_id == Rol.id).filter(
        Rol.nombre.in_(["Administrador", "Arquitecto Manager"])
    ).all()
    
    return render_template("proyectos/crear.html", clientes=clientes, managers=managers)

@proyectos_bp.route("/proyectos/detalle/<int:id>", methods=["GET"])
@login_required
def detalle(id):
    proyecto = Proyecto.query.get_or_404(id)
    
    # Verificación de acceso para Colaboradores Técnicos
    if current_user.rol.nombre == "Colaborador Técnico":
        pertenece = EquipoProyecto.query.filter_by(proyecto_id=id, usuario_id=current_user.id).first()
        if not pertenece:
            flash("No tienes acceso a los detalles de este proyecto.", "danger")
            return redirect(url_for("proyectos.index"))
            
    # Obtener el listado de técnicos disponibles para el formulario de asignación 
    tecnicos = Usuario.query.all()
    return render_template("proyectos/detalle.html", proyecto=proyecto, tecnicos=tecnicos)

@proyectos_bp.route("/proyectos/avance/<int:proyecto_id>", methods=["POST"])
@login_required
def registrar_avance(proyecto_id):
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    
    # Restricción: Los Colaboradores Técnicos pueden registrar avances siempre que pertenezcan al proyecto 
    if current_user.rol.nombre == "Colaborador Técnico":
        pertenece = EquipoProyecto.query.filter_by(proyecto_id=proyecto_id, usuario_id=current_user.id).first()
        if not belongs:
            flash("No estás autorizado para modificar este proyecto.", "danger")
            return redirect(url_for("proyectos.index"))

    porcentaje = int(request.form.get("porcentaje"))
    observacion = request.form.get("observacion")

    if porcentaje < 0 or porcentaje > 100:
        flash("El porcentaje ingresado debe encontrarse en un rango de 0 a 100.", "warning")
        return redirect(url_for("proyectos.detalle", id=proyecto_id))

    if porcentaje > proyecto.avance_actual:
        proyecto.avance_actual = porcentaje

    nuevo_avance = AvanceProyecto(
        proyecto_id=proyecto_id,
        porcentaje=porcentaje,
        observacion=observacion,
        fecha=datetime.now(),
        usuario_id=current_user.id
    )
    db.session.add(nuevo_avance)
    db.session.commit()
    
    registrar_auditoria("REGISTRÓ AVANCE DE OBRA", "avances_proyecto", nuevo_avance.id)
    flash("Historial de avances actualizado correctamente.", "success")
    return redirect(url_for("proyectos.detalle", id=proyecto_id))

