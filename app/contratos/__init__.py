from flask import Blueprint

contratos_bp = Blueprint('contratos', __name__, template_folder='templates')

from app.contratos import routes