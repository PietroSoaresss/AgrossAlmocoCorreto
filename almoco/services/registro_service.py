from datetime import datetime, timedelta
import io
import csv
from models import Registro, db

def registrar_usuario(codigo, nome):
    data_atual = datetime.now().strftime("%Y-%m-%d")

    # Verifica se já existe um registro no mesmo dia
    registro_existente = Registro.query.filter(
        Registro.codigo == codigo,
        Registro.data_hora.like(f"{data_atual}%")
    ).first()

    if registro_existente:
        return {"erro": "Usuário já registrado hoje!"}, 403

    novo_registro = Registro(codigo=codigo, nome=nome)
    db.session.add(novo_registro)
    db.session.commit()

    return {"mensagem": f"Código {codigo} (Nome: {nome}) registrado com sucesso!"}, 200

def gerar_csv(data_inicio, data_fim):
    try:
        data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d")
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

        if data_inicio_obj > data_fim_obj:
            return None, "A data inicial não pode ser maior que a data final."

        registros = Registro.query.filter(
            Registro.data_hora >= data_inicio_obj,
            Registro.data_hora <= data_fim_obj
        ).all()

        if not registros:
            return None, "Nenhum registro encontrado para o período especificado."

        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        writer.writerow(["Código", "Nome", "Data/Hora"])

        for registro in registros:
            writer.writerow([registro.codigo, registro.nome, registro.data_hora])

        writer.writerow([])
        writer.writerow(["Total de Registros", len(registros)])

        output.seek(0)
        return output, None

    except ValueError:
        return None, "Formato de data inválido. Utilize o formato YYYY-MM-DD."
