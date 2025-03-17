from flask import Blueprint, request, jsonify, Response, render_template
from services.registro_service import gerar_csv

downloads_bp = Blueprint('downloads', __name__)

@downloads_bp.route('/download/csv', methods=['GET'])
def download_csv():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')

    if not data_inicio or not data_fim:
        return jsonify({"erro": "Por favor, insira um período válido (data inicial e data final)."}), 400

    output, erro = gerar_csv(data_inicio, data_fim)

    if erro:
        return jsonify({"erro": erro}), 404

    nome_arquivo = f"registros_{data_inicio}_a_{data_fim}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"}
    )

@downloads_bp.route('/downloads', methods=['GET'])
def downloads():
    return render_template("downloads.html")
