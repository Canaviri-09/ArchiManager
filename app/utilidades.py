from functools import wraps
from flask import abort, request
from flask_login import current_user
from app.extensions import db
from app.models_all import Auditoria


def role_required(*roles_permitidos):
    """Decorador que restringe una ruta a los roles indicados.

    Uso:
        @role_required("Administrador")
        @role_required("Administrador", "Arquitecto Manager")
    """
    def decorador(func):
        @wraps(func)
        def envoltura(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.tiene_rol(*roles_permitidos):
                abort(403)
            return func(*args, **kwargs)
        return envoltura
    return decorador


def registrar_auditoria(accion, tabla_afectada, registro_id=None, usuario_id=None):
    """Registra una acción en la tabla de auditoría.

    accion: ej. 'CREÓ', 'MODIFICÓ', 'ELIMINÓ'
    tabla_afectada: nombre de la tabla/entidad afectada
    registro_id: id del registro afectado (opcional)
    usuario_id: si no se indica, se toma del usuario autenticado actual
    """
    if usuario_id is None and current_user.is_authenticated:
        usuario_id = current_user.id

    entrada = Auditoria(
        usuario_id=usuario_id,
        accion=accion,
        tabla_afectada=tabla_afectada,
        registro_id=registro_id,
        ip=request.remote_addr,
    )
    db.session.add(entrada)
    db.session.commit()
