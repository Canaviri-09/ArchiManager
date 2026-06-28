from flask import Blueprint

auditoria_bp = Blueprint('auditoria', __name__, template_folder='templates')

from app.auditoria import routes