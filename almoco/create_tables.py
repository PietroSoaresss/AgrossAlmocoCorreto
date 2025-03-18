# filepath: c:\Users\PietroTI\Documents\workspace\almoco\create_tables.py
from models import db, UsuarioPermitido, Registro
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///presenca.db'  # Substitua pelo URI do seu banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()