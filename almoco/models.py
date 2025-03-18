from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)


class UsuarioPermitido(db.Model):
    __tablename__ = 'usuarios_permitidos'
    codigo = db.Column(db.String(5), primary_key=True)
    nome = db.Column(db.String(50), nullable=False)