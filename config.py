import os
from dotenv import load_dotenv

# Carga las variables de entorno desde el archivo .env
load_dotenv()


class Config:
    # Clave secreta para sesiones y protección CSRF de Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-respaldo-no-usar-en-produccion")

    # Conexión a la base de datos PostgreSQL en Supabase
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Evita conexiones muertas por el pooler de Supabase
    }

    # Configuración de Supabase Storage (carga de archivos en la nube)
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "archimanager-files")

    # Extensiones de archivo permitidas por categoría (Módulo 8. Gestión Documental)
    EXTENSIONES_IMAGEN = {"jpg", "jpeg", "png", "webp"}
    EXTENSIONES_DOCUMENTO = {"pdf"}
    EXTENSIONES_VIDEO = {"mp4"}

    # Tamaño máximo de subida (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
