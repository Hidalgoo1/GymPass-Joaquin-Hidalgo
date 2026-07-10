import os
import re
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from dotenv import load_dotenv
from models import db, Usuario, Socio, Acceso

# Carga de variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración del servidor desde variables de entorno
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

# Parámetros globales de validación
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
PLANES_PERMITIDOS = ['mensual', 'trimestral', 'anual']

# Inicialización de extensiones
db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Inicialización automática de las tablas en la base de datos
with app.app_context():
    db.create_all()


# --- ENDPOINTS DE AUTENTICACIÓN ---

@app.post('/api/auth/register')
def registrar_staff():
    data = request.get_json()

    if not data or 'usuario' not in data or 'password' not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    usuario_input = data['usuario'].strip()
    password_input = data['password']
    rol_input = data.get('rol', 'staff').strip()

    if len(password_input) < 4:
        return jsonify({"error": "La contraseña debe tener al menos 4 caracteres"}), 400

    try:
        if Usuario.query.filter_by(usuario=usuario_input).first():
            return jsonify({"error": "El usuario ya existe"}), 409

        password_encriptada = bcrypt.generate_password_hash(password_input).decode('utf-8')
        nuevo_usuario = Usuario(usuario=usuario_input, password_hash=password_encriptada, rol=rol_input)

        db.session.add(nuevo_usuario)
        db.session.commit()
        return jsonify(nuevo_usuario.to_dict()), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor al registrar"}), 500


@app.post('/api/auth/login')
def login_staff():
    data = request.get_json()

    if not data or 'usuario' not in data or 'password' not in data:
        return jsonify({"error": "Credenciales incompletas"}), 400

    usuario_input = data['usuario'].strip()
    password_input = data['password']

    try:
        usuario = Usuario.query.filter_by(usuario=usuario_input).first()

        if usuario and bcrypt.check_password_hash(usuario.password_hash, password_input):
            token = create_access_token(identity=str(usuario.id))
            return jsonify({"token": token, "usuario": usuario.to_dict()}), 200

        return jsonify({"error": "Usuario o contraseña incorrectos"}), 401

    except Exception:
        return jsonify({"error": "Error interno del servidor al loguear"}), 500


# --- ENDPOINTS CRUD DE SOCIOS ---

@app.get('/api/socios')
def listar_socios():
    try:
        socios = Socio.query.all()
        return jsonify([socio.to_dict() for socio in socios]), 200
    except Exception:
        return jsonify({"error": "Error interno al recuperar la lista de socios"}), 500


@app.get('/api/socios/<int:id>')
def obtener_socio(id):
    try:
        socio = Socio.query.get(id)
        if not socio:
            return jsonify({"error": "Socio no encontrado"}), 404
        return jsonify(socio.to_dict()), 200
    except Exception:
        return jsonify({"error": "Error interno al buscar el socio"}), 500


@app.post('/api/socios')
@jwt_required()
def crear_socio():
    data = request.get_json()

    if not data or not all(k in data for k in ('nombre', 'email', 'dni', 'plan')):
        return jsonify({"error": "Datos obligatorios incompletos"}), 400

    nombre = data['nombre'].strip()
    email = data['email'].strip()
    dni = data['dni'].strip()
    plan = data['plan'].strip().lower()

    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Formato de email invalido"}), 400

    if not dni.isdigit():
        return jsonify({"error": "DNI invalido, debe contener solo numeros"}), 400

    if plan not in PLANES_PERMITIDOS:
        return jsonify({"error": f"Plan invalido. Permitidos: {', '.join(PLANES_PERMITIDOS)}"}), 400

    try:
        if Socio.query.filter_by(email=email).first():
            return jsonify({"error": "El email ya se encuentra registrado"}), 409

        nuevo_socio = Socio(nombre=nombre, email=email, dni=dni, plan=plan, estado="activo")
        db.session.add(nuevo_socio)
        db.session.commit()
        return jsonify(nuevo_socio.to_dict()), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno al registrar el socio"}), 500


@app.patch('/api/socios/<int:id>')
@jwt_required()
def modificar_socio(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos para actualizar"}), 400

    try:
        socio = Socio.query.get(id)
        if not socio:
            return jsonify({"error": "Socio no encontrado"}), 404

        if 'nombre' in data:
            socio.nombre = data['nombre'].strip()

        if 'email' in data:
            email = data['email'].strip()
            if not re.match(EMAIL_REGEX, email):
                return jsonify({"error": "Formato de email invalido"}), 400
            existente = Socio.query.filter_by(email=email).first()
            if existente and existente.id != id:
                return jsonify({"error": "El email ya pertenece a otro socio"}), 409
            socio.email = email

        if 'dni' in data:
            dni = data['dni'].strip()
            if not dni.isdigit():
                return jsonify({"error": "DNI invalido, debe contener solo numeros"}), 400
            socio.dni = dni

        if 'plan' in data:
            plan = data['plan'].strip().lower()
            if plan not in PLANES_PERMITIDOS:
                return jsonify({"error": f"Plan invalido. Permitidos: {', '.join(PLANES_PERMITIDOS)}"}), 400
            socio.plan = plan

        if 'estado' in data:
            estado = data['estado'].strip().lower()
            if estado not in ['activo', 'inactivo']:
                return jsonify({"error": "Estado invalido. Permitidos: activo, inactivo"}), 400
            socio.estado = estado

        db.session.commit()
        return jsonify(socio.to_dict()), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno al actualizar el socio"}), 500


@app.delete('/api/socios/<int:id>')
@jwt_required()
def dar_baja_socio(id):
    try:
        socio = Socio.query.get(id)
        if not socio:
            return jsonify({"error": "Socio no encontrado"}), 404

        socio.estado = "inactivo"
        db.session.commit()
        return jsonify({"mensaje": f"Socio con ID {id} dado de baja exitosamente"}), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno al procesar la baja del socio"}), 500


# --- ENDPOINTS DE CONTROL DE ACCESOS ---

@app.post('/api/accesos')
def registrar_acceso():
    data = request.get_json()

    if not data or 'socio_id' not in data:
        return jsonify({"error": "El parametro socio_id es obligatorio"}), 400

    socio_id_input = data['socio_id']

    try:
        socio = Socio.query.get(socio_id_input)

        # Regla de negocio: Validación de existencia
        if not socio:
            nuevo_acceso = Acceso(socio_id=socio_id_input, resultado="rechazado", motivo="Socio no existe")
            db.session.add(nuevo_acceso)
            db.session.commit()
            return jsonify({"resultado": "rechazado", "motivo": "Socio no existe"}), 404

        # Regla de negocio: Validación de estado administrativo
        if socio.estado.lower() == "inactivo":
            nuevo_acceso = Acceso(socio_id=socio.id, resultado="rechazado", motivo="Socio inactivo")
            db.session.add(nuevo_acceso)
            db.session.commit()
            return jsonify({"resultado": "rechazado", "motivo": "Socio inactivo"}), 400

        # Regla de negocio: Acceso permitido si cumple las condiciones
        nuevo_acceso = Acceso(socio_id=socio.id, resultado="permitido", motivo=None)
        db.session.add(nuevo_acceso)
        db.session.commit()

        return jsonify(nuevo_acceso.to_dict()), 201

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Error interno al procesar el acceso"}), 500


@app.get('/api/accesos')
def listar_accesos():
    socio_id_query = request.args.get('socio_id')

    try:
        if socio_id_query:
            if not socio_id_query.isdigit():
                return jsonify({"error": "El parametro socio_id de busqueda debe ser numerico"}), 400
            accesos = Acceso.query.filter_by(socio_id=int(socio_id_query)).all()
        else:
            accesos = Acceso.query.all()

        return jsonify([acceso.to_dict() for acceso in accesos]), 200

    except Exception:
        return jsonify({"error": "Error interno al recuperar el historial de accesos"}), 500