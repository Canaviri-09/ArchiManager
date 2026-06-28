from flask import Blueprint

documentos_bp = Blueprint('documentos', __name__, template_folder='templates')

from app.documentos import routes