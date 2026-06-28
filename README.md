# ArchiManager

**ArchiManager** es un Sistema Integral de Gestión de Proyectos Arquitectónicos y de Construcción diseñado para centralizar operaciones comerciales, técnicas y administrativas dentro de un estudio profesional. 

La plataforma garantiza la trazabilidad y el control documental absoluto mediante la administración híbrida de datos relacionales y archivos físicos bajo estrictas políticas corporativas y de auditoría.

Este proyecto ha sido desarrollado como entregable principal para la materia **Tecnologías Emergentes II (TEM-742)**.

---

## 🚀 Requisitos Técnicos Implementados

El sistema cumple rigurosamente con los lineamientos académicos y arquitectónicos exigidos en la rúbrica de evaluación:

1. **Patrón de Diseño (Application Factory):** Ciclo de vida y configuraciones de Flask encapsulados herméticamente mediante una función constructora centralizada (`create_app()`).
2. **Sistema de Autenticación Basado en Roles (RBAC):** Control de acceso por cookies de sesión y cifrado Hashing con Bcrypt. Perfiles diferenciados:
   - *Administrador* (Director del estudio)
   - *Arquitecto Manager* (Responsable técnico de obra)
   - *Colaborador Técnico* (Especialistas/Ingenieros de soporte)
3. **Panel Estadístico de Analítica (Dashboard KPIs):** Consumo de funciones agregadas SQL en tiempo real para desplegar indicadores de inversión, volumen documental y el avance físico promedio general de las obras, adaptativo según el rol jerárquico.
4. **Base de Datos Relacional Normalizada:** Implementación de un motor robusto **PostgreSQL (Supabase)** estructurado en Tercera Forma Normal (3FN) que consta de 10 tablas interconectadas para modelar el negocio.
5. **Operaciones CRUD Completas:** Interfaces dinámicas para altas, bajas, lecturas y modificaciones de Usuarios, Clientes, Proyectos, Contratos y Documentación.
6. **Mecanismos Avanzados de Negocio:**
   - *Borrado Lógico*: Flag `eliminado=True` para preservar el histórico e integridad física de planos y archivos técnicos.
   - *Control de Versionado Automático*: Almacenamiento secuencial incremental (`v1`, `v2`, etc.) al actualizar la documentación técnica.
   - *Bitácora de Auditoría Global*: Registro instantáneo de operaciones de base de datos exclusivo para el rol de administración.
7. **Interfaz de Usuario (UI/UX):** Capa de presentación completamente responsiva desarrollada con Bootstrap 5, Jinja2 y alertas de estado dinámicas.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python 3.12, Flask Framework.
- **ORM & Base de Datos:** Flask-SQLAlchemy, Psycopg2, PostgreSQL (Supabase Cloud).
- **Seguridad:** Flask-Login, Flask-Bcrypt (Cifrado Blowfish).
- **Frontend:** Bootstrap 5, Jinja2 Templates, HTML5, CSS3.

---

## 📁 Estructura de la Arquitectura (MVC Modular)

```text
archimanager/
├── app/
│   ├── __init__.py          # Inicialización centralizada (Application Factory)
│   ├── extensions.py        # Instancia global de componentes (DB, Bcrypt, Login)
│   ├── models_all.py        # Mapeo ORM unificado de las 10 entidades SQL
│   ├── utilidades.py        # Helpers globales (Ej: Generador de Auditorías)
│   │
│   ├── auth/                # Blueprint de Autenticación y Sesiones
│   ├── usuarios/            # Blueprint para el CRUD de Personal Técnico
│   ├── clientes/            # Blueprint de Gestión de Cuentas Comerciales
│   ├── proyectos/           # Blueprint de Obras, Equipos y Avance Físico
│   ├── contratos/           # Blueprint de Documentos Legales y Carga de PDFs
│   ├── documentos/          # Blueprint de Planos Técnicos con Versionado
│   ├── auditoria/           # Blueprint de Bitácora de Eventos (Exclusivo Admin)
│   ├── dashboard/           # Blueprint Analítico del Panel de Control
│   │
│   ├── templates/           # Vistas Maestras e Inyecciones Contextuales
│   └── static/              # Archivos Estáticos (Estilos CSS y Almacenamiento de Cargas)
├── config.py
├── requirements.txt         # Dependencias del Entorno Virtual
├── run.py                   # Servidor de Producción / Punto de Entrada
└── semillero.py             # Script de Poblado Inicial de la Base de Datos
```

---

## ⚙️ Instalación y Configuración

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local:

1. **Clonar o descargar el proyecto** en tu máquina.

2. **Crear y activar el entorno virtual (`venv`):**
   - En **Windows**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - En **Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Instalar dependencias requeridas:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno (`.env`):**
   Crea un archivo llamado `.env` en la raíz del proyecto con la siguiente configuración:
   ```env
   DATABASE_URL="postgresql://usuario:contraseña@host:puerto/nombre_db"
   SECRET_KEY="tu_clave_secreta_aqui"
   SUPABASE_URL="https://tu_proyecto.supabase.co"
   SUPABASE_SERVICE_ROLE_KEY="tu_clave_de_rol_de_servicio_aqui"
   SUPABASE_BUCKET="tu_nombre_de_bucket"
   FLASK_DEBUG=True
   ```
   > [!IMPORTANT]
   > Asegúrate de que el `DATABASE_URL` no termine con el parámetro `?pgbouncer=true` si utilizas SQLAlchemy y psycopg2 directamente, para evitar errores de conexión (`ProgrammingError: invalid connection option "pgbouncer"`).

5. **Poblar la Base de Datos (Semillero):**
   Antes de ejecutar la aplicación, debes poblar los roles, especialidades, tipos de contrato y crear el usuario administrador ejecutando:
   ```bash
   python semillero.py
   ```

6. **Ejecutar el Servidor de Desarrollo:**
   Inicia la aplicación de Flask localmente:
   ```bash
   python run.py
   ```
   El sistema estará activo en: [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

## 🔑 Credenciales del Administrador por Defecto

* **Correo:** `admin@archimanager.com`
* **Contraseña:** `admin123`