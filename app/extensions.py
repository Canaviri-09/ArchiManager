from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from supabase import create_client

# Inicialización de extensiones (sin app todavía, se enlazan en create_app)
db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Debes iniciar sesión para acceder a esta página."
login_manager.login_message_category = "warning"


def crear_cliente_supabase(app):
    """Crea el cliente de Supabase Storage usando la service_role key.

    Se usa la service_role key porque el backend es el único que sube y
    gestiona archivos; el control de quién puede subir/borrar se hace en
    Flask mediante los roles, no mediante políticas RLS de Supabase.
    """
    url = app.config["SUPABASE_URL"]
    key = app.config["SUPABASE_SERVICE_ROLE_KEY"]
    if not url or not key:
        return None
    return create_client(url, key)
