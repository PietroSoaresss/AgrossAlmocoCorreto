from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(5), nullable=False)
    nome = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Registro {self.nome}>'
    