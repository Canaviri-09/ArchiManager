from flask import Blueprint

proyectos_bp = Blueprint('proyectos', __name__, template_folder='templates')

from app.proyectos import routes