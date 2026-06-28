from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class Rol(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship("Usuario", backref="rol", lazy=True)


class Especialidad(db.Model):
    __tablename__ = "especialidades"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'Arquitectura' | 'Ingeniería'

    usuarios = db.relationship("Usuario", backref="especialidad", lazy=True)


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey("especialidades.id"), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)

    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        # Flask-Login usa is_active para impedir el login de usuarios desactivados
        return self.activo

    def tiene_rol(self, *nombres_rol):
        return self.rol is not None and self.rol.nombre in nombres_rol


class Cliente(db.Model):
    __tablename__ = "clientes"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    empresa = db.Column(db.String(150), nullable=True)
    telefono = db.Column(db.String(30), nullable=True)
    correo = db.Column(db.String(150), nullable=True)
    nit = db.Column(db.String(30), nullable=True)

    proyectos = db.relationship("Proyecto", backref="cliente", lazy=True)


class Proyecto(db.Model):
    __tablename__ = "proyectos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    presupuesto = db.Column(db.Numeric(14, 2), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="Diseño")
    avance_actual = db.Column(db.Integer, nullable=False, default=0)
    responsable_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    portada_url = db.Column(db.String(500), nullable=True)

    responsable = db.relationship("Usuario", foreign_keys=[responsable_id])
    equipo = db.relationship("EquipoProyecto", backref="proyecto", lazy=True, cascade="all, delete-orphan")
    ubicacion = db.relationship("Ubicacion", backref="proyecto", uselist=False, cascade="all, delete-orphan")
    contratos = db.relationship("Contrato", backref="proyecto", lazy=True, cascade="all, delete-orphan")
    archivos = db.relationship("Archivo", backref="proyecto", lazy=True, cascade="all, delete-orphan")
    avances = db.relationship("AvanceProyecto", backref="proyecto", lazy=True, cascade="all, delete-orphan")


class EquipoProyecto(db.Model):
    __tablename__ = "equipos_proyecto"

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    funcion = db.Column(db.String(100), nullable=True)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship("Usuario")


class Ubicacion(db.Model):
    __tablename__ = "ubicaciones"

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), unique=True, nullable=False)
    pais = db.Column(db.String(100), nullable=True)
    departamento = db.Column(db.String(100), nullable=True)
    municipio = db.Column(db.String(100), nullable=True)
    zona = db.Column(db.String(100), nullable=True)
    calle = db.Column(db.String(150), nullable=True)
    numero = db.Column(db.String(20), nullable=True)
    latitud = db.Column(db.Numeric(10, 6), nullable=True)
    longitud = db.Column(db.Numeric(10, 6), nullable=True)


class TipoContrato(db.Model):
    __tablename__ = "tipos_contrato"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    contratos = db.relationship("Contrato", backref="tipo_contrato", lazy=True)


class Contrato(db.Model):
    __tablename__ = "contratos"

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    tipo_contrato_id = db.Column(db.Integer, db.ForeignKey("tipos_contrato.id"), nullable=False)
    numero_contrato = db.Column(db.String(50), nullable=False)
    fecha_firma = db.Column(db.Date, nullable=True)
    archivo_pdf = db.Column(db.String(500), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="Activo")


class Archivo(db.Model):
    __tablename__ = "archivos"

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    nombre = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'imagen' | 'documento' | 'video'
    url = db.Column(db.String(500), nullable=False)
    version_actual = db.Column(db.Integer, nullable=False, default=1)
    eliminado = db.Column(db.Boolean, nullable=False, default=False)

    autor = db.relationship("Usuario")
    versiones = db.relationship("VersionArchivo", backref="archivo", lazy=True, cascade="all, delete-orphan")


class VersionArchivo(db.Model):
    __tablename__ = "versiones_archivos"

    id = db.Column(db.Integer, primary_key=True)
    archivo_id = db.Column(db.Integer, db.ForeignKey("archivos.id"), nullable=False)
    version = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500), nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    autor = db.relationship("Usuario")


class AvanceProyecto(db.Model):
    __tablename__ = "avances_proyecto"

    id = db.Column(db.Integer, primary_key=True)
    proyecto_id = db.Column(db.Integer, db.ForeignKey("proyectos.id"), nullable=False)
    porcentaje = db.Column(db.Integer, nullable=False)
    observacion = db.Column(db.Text, nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    usuario = db.relationship("Usuario")


class Auditoria(db.Model):
    __tablename__ = "auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    accion = db.Column(db.String(50), nullable=False)
    tabla_afectada = db.Column(db.String(50), nullable=False)
    registro_id = db.Column(db.Integer, nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String(45), nullable=True)

    usuario = db.relationship("Usuario")
