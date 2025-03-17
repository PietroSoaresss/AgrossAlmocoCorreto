from datetime import datetime, timedelta
import io
import csv
from models import Registro, db
from flask import current_app
from models import db


# Lista de códigos permitidos (substitua pelos códigos corretos)
USUARIOS_PERMITIDOS = {
    
    '11111':'Pietro Soares',
    '22222':'Maria Silva',
    '12345':'João Silva',
    '54321':'Marcos Martins',
    '33333':'Pedro Soares'
    
    
}  # Exemplo de códigos autorizados

from datetime import datetime
from flask import current_app
from models import Registro, db


def registrar_usuario(codigo, nome):
    with current_app.app_context():  # Garante que estamos dentro do contexto do Flask
        
        # Verifica se o usuário está na lista permitida
        if codigo not in USUARIOS_PERMITIDOS:
            return {"erro": "Usuário não autorizado!"}, 403

        data_atual = datetime.now().replace(microsecond=0)  

        # Verifica se já existe um registro no mesmo dia
        registro_existente = Registro.query.filter(
            Registro.codigo == codigo,
            db.func.date(Registro.data_hora) == data_atual.date()  
        ).first()

        if registro_existente:
            return {"erro": "Usuário já registrado hoje!"}, 403

        
        novo_registro = Registro(
            codigo=codigo,
            nome=nome,
            data_hora=data_atual  
        )
        db.session.add(novo_registro)

        try:
            db.session.commit()
            return {"mensagem": f"Código {codigo} (Nome: {nome}) registrado com sucesso!"}, 200
        except Exception as e:
            db.session.rollback()
            return {"erro": str(e)}, 500


def gerar_csv(data_inicio, data_fim):
    try:
        # Converte as datas fornecidas para objetos datetime
        data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d")
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

        if data_inicio_obj > data_fim_obj:
            return None, "A data inicial não pode ser maior que a data final."

        # Consulta os registros entre as datas fornecidas
        registros = Registro.query.filter(
            Registro.data_hora >= data_inicio_obj,
            Registro.data_hora <= data_fim_obj
        ).all()

        if not registros:
            return None, "Nenhum registro encontrado para o período especificado."

        # Prepara o arquivo CSV em memória
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')

        # Escreve o cabeçalho do CSV
        writer.writerow(["Código", "Nome", "Data/Hora"])

        # Escreve os dados dos registros
        for registro in registros:
            # Formata a data e hora completa para ser exibida no CSV com \t antes da data
            if registro.data_hora:
                data_hora_formatada = f"\t{registro.data_hora.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                data_hora_formatada = "\tData não disponível"

            # Escreve uma linha no CSV com os dados formatados
            writer.writerow([registro.codigo, registro.nome, data_hora_formatada])

        # Escreve o total de registros no final
        writer.writerow([])  # Linha em branco
        writer.writerow(["Total de Registros", len(registros)])

        # Retorna o arquivo CSV gerado
        output.seek(0)
        return output, None

    except ValueError:
        return None, "Formato de data inválido. Utilize o formato YYYY-MM-DD."