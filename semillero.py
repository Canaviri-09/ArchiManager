from app import create_app
from app.extensions import db, bcrypt
from app.models_all import Rol, Especialidad, TipoContrato, Usuario

app = create_app()

ROLES = ["Administrador", "Arquitecto Manager", "Colaborador Técnico"]

ESPECIALIDADES = [
    ("Arquitecto Proyectista", "Arquitectura"),
    ("Arquitecto de Interiores", "Arquitectura"),
    ("Arquitecto Paisajista", "Arquitectura"),
    ("Arquitecto Supervisor de Obra", "Arquitectura"),
    ("Arquitecto Técnico / Director de Obra", "Arquitectura"),
    ("Ingeniero Civil", "Ingeniería"),
    ("Ingeniero Estructural", "Ingeniería"),
    ("Ingeniero Eléctrico", "Ingeniería"),
    ("Ingeniero Sanitario", "Ingeniería"),
]

TIPOS_CONTRATO = [
    "Diseño Arquitectónico",
    "Llave en Mano",
    "Supervisión",
    "Consultoría",
]

ADMIN_CORREO = "admin@archimanager.com"
ADMIN_PASSWORD = "admin123"


def poblar_roles():
    creados = 0
    for nombre in ROLES:
        if not Rol.query.filter_by(nombre=nombre).first():
            db.session.add(Rol(nombre=nombre))
            creados += 1
    db.session.commit()
    print(f"Roles: {creados} insertados (de {len(ROLES)} definidos).")


def poblar_especialidades():
    creados = 0
    for nombre, tipo in ESPECIALIDADES:
        if not Especialidad.query.filter_by(nombre=nombre).first():
            db.session.add(Especialidad(nombre=nombre, tipo=tipo))
            creados += 1
    db.session.commit()
    print(f"Especialidades: {creados} insertadas (de {len(ESPECIALIDADES)} definidas).")


def poblar_tipos_contrato():
    creados = 0
    for nombre in TIPOS_CONTRATO:
        if not TipoContrato.query.filter_by(nombre=nombre).first():
            db.session.add(TipoContrato(nombre=nombre))
            creados += 1
    db.session.commit()
    print(f"Tipos de contrato: {creados} insertados (de {len(TIPOS_CONTRATO)} definidos).")


def poblar_admin():
    if Usuario.query.filter_by(correo=ADMIN_CORREO).first():
        print("Usuario Administrador semilla ya existe, no se duplica.")
        return

    rol_admin = Rol.query.filter_by(nombre="Administrador").first()
    if not rol_admin:
        print("ERROR: el rol 'Administrador' no existe. Ejecuta poblar_roles() primero.")
        return

    hashed = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode("utf-8")
    admin = Usuario(
        nombre="Administrador del Sistema",
        correo=ADMIN_CORREO,
        password=hashed,
        rol_id=rol_admin.id,
        especialidad_id=None,
        activo=True,
    )
    db.session.add(admin)
    db.session.commit()
    print(f"Usuario Administrador creado -> correo: {ADMIN_CORREO} / password: {ADMIN_PASSWORD}")


def main():
    with app.app_context():
        print("Creando tablas en la base de datos (si no existen)...")
        db.create_all()
        print("Tablas verificadas/creadas correctamente.\n")

        poblar_roles()
        poblar_especialidades()
        poblar_tipos_contrato()
        poblar_admin()

        print("\nSemillero ejecutado correctamente.")


if __name__ == "__main__":
    main()
