import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from dotenv import load_dotenv
from models import db, Usuario

# Carga de variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración del servidor desde variables de entorno
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

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