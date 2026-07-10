from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(30), nullable=False, default="staff")

    def to_dict(self):
        return {
            "id": self.id,
            "usuario": self.usuario,
            "rol": self.rol
        }


class Socio(db.Model):
    __tablename__ = 'socios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    dni = db.Column(db.String(20), nullable=False)
    plan = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default="activo")
    fecha_alta = db.Column(db.DateTime, nullable=False, default=datetime.now)

    accesos = db.relationship('Acceso', backref='socio', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "dni": self.dni,
            "plan": self.plan,
            "estado": self.estado,
            "fecha_alta": self.fecha_alta.strftime('%Y-%m-%d %H:%M:%S')
        }


class Acceso(db.Model):
    __tablename__ = 'accesos'

    id = db.Column(db.Integer, primary_key=True)
    socio_id = db.Column(db.Integer, db.ForeignKey('socios.id', ondelete="CASCADE"), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.now)
    resultado = db.Column(db.String(20), nullable=False)
    motivo = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "socio_id": self.socio_id,
            "fecha_hora": self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
            "resultado": self.resultado,
            "motivo": self.motivo
        }