from flask import Flask
from app.extensions import db, bcrypt, login_manager, crear_cliente_supabase


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Inicializar extensiones con la app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Supabase Storage 
    app.extensions["supabase"] = crear_cliente_supabase(app)

    # Importar modelos para que SQLAlchemy los registre antes de create_all
    from app import models_all  

    @login_manager.user_loader
    def load_user(user_id):
        from app.models_all import Usuario
        return Usuario.query.get(int(user_id))

    # --- Registro de Blueprints ---
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.clientes import clientes_bp
    app.register_blueprint(clientes_bp)

    from app.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    from app.proyectos import proyectos_bp
    app.register_blueprint(proyectos_bp)
    
    from app.contratos import contratos_bp
    app.register_blueprint(contratos_bp)
    
    from app.documentos import documentos_bp
    app.register_blueprint(documentos_bp)
    
    from app.auditoria import auditoria_bp
    app.register_blueprint(auditoria_bp)
    
    with app.app_context():
        db.create_all()

    
    return app
