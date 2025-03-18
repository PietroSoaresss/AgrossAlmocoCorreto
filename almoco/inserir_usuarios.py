# filepath: c:\Users\PietroTI\Documents\workspace\almoco\inserir_usuarios.py
from models import db, UsuarioPermitido
from flask import Flask

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///presenca.db'  # Substitua pelo URI do seu banco de dados
db.init_app(app)

usuarios_permitidos = [
  
    {"codigo": "55555", "nome": "Jose Martins"}
]

with app.app_context():
    for usuario in usuarios_permitidos:
        novo_usuario = UsuarioPermitido(codigo=usuario["codigo"], nome=usuario["nome"])
        db.session.add(novo_usuario)
    db.session.commit()