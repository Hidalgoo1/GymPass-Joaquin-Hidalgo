# GymPass - API de Gestión de Socios y Accesos

Backend desarrollado en Python con el framework Flask para la gestión centralizada de socios, control de accesos automatizado y seguridad criptográfica mediante tokens stateless.

## Stack Tecnológico Exigido
* Python 3.x
* Flask
* Flask-SQLAlchemy (ORM)
* Flask-Bcrypt
* Flask-JWT-Extended
* Requests

## Estructura de Endpoints Disponibles

### Autenticación y Seguridad (Públicos)
* `POST /api/auth/register` - Registro de personal del staff.
* `POST /api/auth/login` - Login de staff. Devuelve el token JWT necesario para operar.

### Gestión de Socios (Protegidos con JWT)
* `GET /api/socios` - Lista la totalidad de los socios registrados.
* `GET /api/socios/<id>` - Recupera la información de un socio específico.
* `POST /api/socios` - Alta de un nuevo socio con validaciones en servidor.
* `PATCH /api/socios/<id>` - Modificación parcial de datos del socio.
* `DELETE /api/socios/<id>` - Baja lógica del socio (cambio a estado inactivo).

### Control de Accesos (Públicos / Integración)
* `POST /api/accesos` - Registra el intento de entrada de un socio, valida su estado e internaliza datos climáticos por patrón proxy.
* `GET /api/accesos` - Historial general de accesos. Permite filtrar por query param `?socio_id=ID`.

## Instrucciones de Instalación y Despliegue de Cero

Siga estrictamente estos pasos para inicializar el entorno y ejecutar la aplicación en un entorno limpio:

### 1. Clonar el repositorio e ingresar al directorio

```bash
git clone https://github.com/Hidalgoo1/GymPass-Joaquin-Hidalgo.git
cd GymPass-Joaquin-Hidalgo
```

### 2. Crear y activar el entorno virtual (venv)

```bash
python -m venv .venv
# En Windows:
.\.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
```

### 3. Instalar la totalidad de dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno 
Copie el archivo de ejemplo y configure las claves correspondientes en el archivo .env generado (el cual se encuentra excluido del versionado):

```bash
cp .env.example .env
```

### 5. Ejecutar la aplicacion
El servidor inicializará de forma automática las tablas de la base de datos relacional SQLite (gympass.db) en su primera ejecución:

```bash
python app.py
```

### Credenciales de prueba sugeridas
Para facilitar la demostración de la API en Postman o cURL, se sugiere registrar un usuario inicial o utilizar peticiones directas al endpoint de login tras darlo de alta en la base local.

* Usuario de Staff: admin_gym
* Contraseña de Staff: secret123