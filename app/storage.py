import uuid
import mimetypes
from flask import current_app


def _cliente():
    return current_app.extensions.get("supabase")


def _bucket():
    return current_app.config.get("SUPABASE_BUCKET", "Files")


def subir_archivo(archivo_stream, nombre_original, carpeta="general"):
   
    cliente = _cliente()
    if not cliente:
        current_app.logger.error("Cliente Supabase no inicializado.")
        return None

    ext = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else "bin"
    nombre_unico = f"{carpeta}/{uuid.uuid4().hex}.{ext}"

    content_type = mimetypes.guess_type(nombre_original)[0] or "application/octet-stream"

    datos = archivo_stream.read()

    try:
        cliente.storage.from_(_bucket()).upload(
            path=nombre_unico,
            file=datos,
            file_options={"content-type": content_type},
        )
        url = cliente.storage.from_(_bucket()).get_public_url(nombre_unico)
        return url
    except Exception as e:
        current_app.logger.error(f"Error subiendo archivo a Supabase Storage: {e}")
        return None


def eliminar_archivo(url):
    
    cliente = _cliente()
    if not cliente or not url:
        return False

    try:
        bucket = _bucket()
        # Extraer el path relativo desde la URL pública
        # URL típica: https://<proyecto>.supabase.co/storage/v1/object/public/<bucket>/<path>
        marcador = f"/object/public/{bucket}/"
        idx = url.find(marcador)
        if idx == -1:
            return False
        path = url[idx + len(marcador):]
        cliente.storage.from_(bucket).remove([path])
        return True
    except Exception as e:
        current_app.logger.error(f"Error eliminando archivo de Supabase Storage: {e}")
        return False


def extension_valida(nombre_archivo, tipos_permitidos):
    
    if "." not in nombre_archivo:
        return False
    ext = nombre_archivo.rsplit(".", 1)[-1].lower()
    return ext in tipos_permitidos
