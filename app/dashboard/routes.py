from flask import render_template
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.extensions import db
from app.models_all import Proyecto, Cliente, Usuario, Archivo, EquipoProyecto

@dashboard_bp.route("/dashboard")
@dashboard_bp.route("/")
@login_required
def index():
    rol = current_user.rol.nombre

    # 1. ESCENARIO: EL ADMINISTRADOR (Métricas Globales de la Empresa)
    if rol == "Administrador":
        total_proyectos = Proyecto.query.count()
        total_clientes = Cliente.query.count()
        total_usuarios = Usuario.query.count()
        total_archivos = Archivo.query.filter_by(eliminado=False).count()
        
        # Inversión Total (Suma de presupuestos)
        presupuesto_total = db.session.query(db.func.sum(Proyecto.presupuesto)).scalar() or 0.0
        
        # Avance Promedio de todos los proyectos del estudio
        avance_promedio = db.session.query(db.func.avg(Proyecto.avance_actual)).scalar() or 0.0
        
        # Listado general de control
        proyectos_recientes = Proyecto.query.order_by(Proyecto.id.desc()).limit(5).all()

    # 2. ESCENARIO: ARQUITECTO MANAGER (Métricas de sus proyectos a cargo)
    elif rol == "Arquitecto Manager":
        total_proyectos = Proyecto.query.filter_by(responsable_id=current_user.id).count()
        total_clientes = db.session.query(db.func.count(db.func.distinct(Proyecto.cliente_id))).filter(Proyecto.responsable_id == current_user.id).scalar() or 0
        total_usuarios = Usuario.query.filter_by(activo=True).count() # Contexto general
        total_archivos = Archivo.query.join(Proyecto).filter(Proyecto.responsable_id == current_user.id, Archivo.eliminado == False).count()
        
        presupuesto_total = db.session.query(db.func.sum(Proyecto.presupuesto)).filter(Proyecto.responsable_id == current_user.id).scalar() or 0.0
        avance_promedio = db.session.query(db.func.avg(Proyecto.avance_actual)).filter(Proyecto.responsable_id == current_user.id).scalar() or 0.0
        
        proyectos_recientes = Proyecto.query.filter_by(responsable_id=current_user.id).order_by(Proyecto.id.desc()).all()

    # 3. ESCENARIO: COLABORADOR TÉCNICO (Métricas simplificadas de sus asignaciones)
    else:
        # Proyectos donde participa como miembro de equipo
        proyectos_vinculados = Proyecto.query.join(EquipoProyecto).filter(EquipoProyecto.usuario_id == current_user.id).all()
        
        total_proyectos = len(proyectos_vinculados)
        total_clientes = len(set([p.cliente_id for p in proyectos_vinculados]))
        total_usuarios = len(proyectos_vinculados) # Relativo a sus entornos de equipo
        total_archivos = Archivo.query.filter_by(usuario_id=current_user.id, eliminado=False).count()
        
        presupuesto_total = sum([p.presupuesto for p in proyectos_vinculados]) if proyectos_vinculados else 0.0
        
        avances = [p.avance_actual for p in proyectos_vinculados] if proyectos_vinculados else []
        avance_promedio = sum(avances) / len(avances) if avances else 0.0
        
        proyectos_recientes = proyectos_vinculados

    return render_template(
        "dashboard/index.html",
        total_proyectos=total_proyectos,
        total_clientes=total_clientes,
        total_usuarios=total_usuarios,
        total_archivos=total_archivos,
        presupuesto_total=presupuesto_total,
        avance_promedio=round(avance_promedio, 2),
        proyectos_recientes=proyectos_recientes,
        rol_usuario=rol
    )
