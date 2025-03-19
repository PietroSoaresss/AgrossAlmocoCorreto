from flask import Flask, request, jsonify, Response, render_template, redirect, url_for, flash
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import csv
import io
from sqlalchemy import func

app = Flask(__name__)

# Configuração do banco de dados PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345@localhost:5432/registros'  # Ajuste conforme suas credenciais
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

# Configurando SQLAlchemy
db = SQLAlchemy(app)

# Definindo o modelo de Registro
class Registro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Criar as tabelas no banco de dados
with app.app_context():
    db.create_all()

# Dicionário com usuários permitidos
USUARIOS_PERMITIDOS = {
    "12345": "João Silva",
    "67890": "Maria Oliveira",
    "54321": "Carlos Souza",
    "11111": "Pietro Soares",
    "22222": "Marcos da Silva Abreu",
    "33333": "João Pedro Henrique Martins da Silva da Costa"
}

# Estabelecendo conexão manualmente com psycopg2
@app.after_request
def after_request(response):
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

# Criação do banco de dados
@app.route('/')
def index():
    db.create_all()  # Criar todas as tabelas no banco de dados
    return render_template("index.html")

# Rota para registrar presença
@app.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    codigo_completo = data.get("codigo")

    if not codigo_completo:
        return jsonify({"erro": "Código é obrigatório"}), 400

    partes = codigo_completo.split(";")
    if len(partes) < 2:
        return jsonify({"erro": "Formato inválido. Use 'codigo;nome'"}), 400

    codigo, nome = partes[0], partes[1]

    if codigo not in USUARIOS_PERMITIDOS or USUARIOS_PERMITIDOS[codigo] != nome:
        return jsonify({"erro": "Usuário não permitido!"}), 403

    data_atual = datetime.now().strftime("%Y-%m-%d")

    # Verifica se o usuário já registrou presença no dia
    registro_existente = Registro.query.filter(
        Registro.codigo == codigo,
        Registro.data_hora.like(f"{data_atual}%")
    ).first()

    if registro_existente:
        return jsonify({"erro": "Usuário já registrado hoje!"}), 403

    # Cria um novo registro
    novo_registro = Registro(codigo=codigo, nome=nome)
    db.session.add(novo_registro)
    db.session.commit()

    return jsonify({"mensagem": f"Código {codigo} (Nome: {nome}) registrado com sucesso!"})

# Rota para consultar registros
@app.route('/banco', methods=['GET'])
def banco():
    data_filtro = request.args.get('data')

    query = Registro.query

    if data_filtro:
        query = query.filter(func.date(Registro.data_hora) == data_filtro)

    registros = query.order_by(Registro.data_hora.desc()).all()

    resultado = [{"codigo": r.codigo, "nome": r.nome, "data_hora": r.data_hora} for r in registros]
    return jsonify(resultado)

# Rota para download de registros em formato CSV
@app.route('/download/csv', methods=['GET'])
def download_csv():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not data_inicio or not data_fim:
        return jsonify({"erro": "Por favor, insira um período válido (data inicial e data final)."}), 400

    try:
        data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d")
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

        if data_inicio_obj > data_fim_obj:
            return jsonify({"erro": "A data inicial não pode ser maior que a data final."}), 400

        registros = Registro.query.filter(
            Registro.data_hora >= data_inicio_obj,
            Registro.data_hora <= data_fim_obj
        ).all()

        if not registros:
            return jsonify({"erro": "Nenhum registro encontrado para o período especificado."}), 404

        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Cabeçalho do CSV
        writer.writerow(["Código", "Nome", "Data/Hora"])

        for registro in registros:
            writer.writerow([registro.codigo, registro.nome, registro.data_hora])

        output.seek(0)

        nome_arquivo = f"registros_{data_inicio}_a_{data_fim}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
        )
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Utilize o formato YYYY-MM-DD."}), 400

# Rota para a página de downloads
@app.route('/downloads', methods=['GET'])
def downloads():
    return render_template("downloads.html")

# Rota para exibir registros com filtros e paginação
@app.route('/registros', methods=['GET'])
def registros():
    data_filtro = request.args.get('data')
    nome_filtro = request.args.get('nome')
    codigo_filtro = request.args.get('codigo')
    page = request.args.get('page', 1, type=int)  # Página padrão 1
    per_page = 10  # Registros por página

    query = Registro.query.order_by(Registro.data_hora.desc())

    if data_filtro:
        try:
            data_filtro_formatada = datetime.strptime(data_filtro, "%Y-%m-%d").date()
            query = query.filter(func.date(Registro.data_hora) == data_filtro_formatada)
        except ValueError:
            flash("Formato de data inválido. Use YYYY-MM-DD.", "error")

    if nome_filtro:
        query = query.filter(Registro.nome.ilike(f"%{nome_filtro}%"))

    if codigo_filtro:
        query = query.filter(Registro.codigo.ilike(f"%{codigo_filtro}%"))

    registros_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        'consulta.html',
        registros=registros_paginados.items,
        page=registros_paginados.page,
        total_pages=registros_paginados.pages
    )

if __name__ == "__main__":
    app.run(debug=True)