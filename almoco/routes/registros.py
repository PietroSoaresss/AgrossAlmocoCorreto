from flask import Blueprint, request, jsonify, render_template, flash
from services.registro_service import registrar_usuario
from models import Registro
from datetime import datetime
from sqlalchemy import func

registros_bp = Blueprint('registros', __name__)

@registros_bp.route('/')
def index():
    return render_template("index.html")


@registros_bp.route('/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    codigo_completo = data.get("codigo")

    if not codigo_completo:
        return jsonify({"erro": "Código é obrigatório"}), 400

    partes = codigo_completo.split(";")
    if len(partes) < 2:
        return jsonify({"erro": "Formato inválido. Use 'codigo;nome'"}), 400

    codigo, nome = partes[0], partes[1]
    resposta, status_code = registrar_usuario(codigo, nome)
    
    return jsonify(resposta), status_code

@registros_bp.route('/registros', methods=['GET'])
def registros():
    try:
        # Pegando os parâmetros de filtro e página
        data_filtro = request.args.get('data')
        nome_filtro = request.args.get('nome')
        codigo_filtro = request.args.get('codigo')
        page = request.args.get('page', 1, type=int)
        per_page = 10  # Limite de registros por página

        # Consultar a base de dados
        query = Registro.query.order_by(Registro.data_hora.desc())

        # Filtros para data
        if data_filtro:
            if data_filtro.isdigit():  # Verifica se contém apenas números
                if len(data_filtro) == 4:  # Ano completo (YYYY)
                    query = query.filter(func.extract('year', Registro.data_hora) == int(data_filtro))
                elif len(data_filtro) <= 2:  # Apenas o dia (1 ou 2 dígitos)
                    query = query.filter(func.extract('day', Registro.data_hora) == int(data_filtro))
                elif len(data_filtro) == 7:  # Formato mês (YYYY-MM)
                    try:
                        query = query.filter(func.extract('month', Registro.data_hora) == int(data_filtro.split('-')[1]))
                    except Exception as e:
                        flash(f"Erro no filtro de mês: {str(e)}", "error")
                else:
                    flash("Formato de data inválido. Use YYYY, YYYY-MM ou YYYY-MM-DD.", "error")
            else:
                try:
                    # Formato completo YYYY-MM-DD
                    data_filtro_formatada = datetime.strptime(data_filtro, "%Y-%m-%d").date()
                    query = query.filter(func.date(Registro.data_hora) == data_filtro_formatada)
                except ValueError:
                    flash("Formato de data inválido. Use YYYY-MM-DD, apenas o ano (YYYY), mês (YYYY-MM) ou apenas o dia (DD).", "error")

        # Filtro para nome
        if nome_filtro:
            query = query.filter(Registro.nome.ilike(f"%{nome_filtro}%"))

        # Filtro para código
        if codigo_filtro:
            query = query.filter(Registro.codigo.ilike(f"%{codigo_filtro}%"))

        # Paginação
        registros_paginados = query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template(
            'consulta.html',
            registros=registros_paginados.items,  # Registros da página atual
            page=registros_paginados.page,        # Página atual
            total_pages=registros_paginados.pages,  # Total de páginas
            data_filtro=data_filtro,  # Passando filtro para a URL
            nome_filtro=nome_filtro,  # Passando filtro para a URL
            codigo_filtro=codigo_filtro  # Passando filtro para a URL
        )

    except Exception as e:
        return jsonify({"erro": str(e)}), 500