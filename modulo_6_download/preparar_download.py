import os
import shutil
from datetime import datetime


def normalizar_nome_arquivo(texto):
    texto = str(texto).strip().lower()

    substituicoes = {
        " ": "_",
        "-": "_",
        "/": "_",
        "\\": "_",
        ".": "_",
        "ç": "c",
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "é": "e",
        "ê": "e",
        "í": "i",
        "ó": "o",
        "õ": "o",
        "ô": "o",
        "ú": "u",
    }

    for antigo, novo in substituicoes.items():
        texto = texto.replace(antigo, novo)

    while "__" in texto:
        texto = texto.replace("__", "_")

    return texto.strip("_")


def obter_data_referencia(df_conciliado):
    """
    Pega uma data de referência para montar o nome do arquivo final.

    Prioridade:
    1. data_pagamento_instituicao   -> data real de recebimento/pagamento
    2. data_vencimento_instituicao  -> data prevista de recebimento
    3. data_venda_instituicao       -> data da venda
    4. data atual                   -> fallback de segurança
    """

    colunas_data = [
        "data_pagamento_instituicao",
        "data_vencimento_instituicao",
        "data_venda_instituicao",
    ]

    for coluna in colunas_data:
        if coluna in df_conciliado.columns:
            datas_validas = df_conciliado[coluna].dropna()

            if not datas_validas.empty:
                return datas_validas.min()

    return datetime.now()




def formatar_data_nome_arquivo(data_referencia):
    data_referencia = datetime.strptime(
        str(data_referencia.date()),
        "%Y-%m-%d"
    )

    ano = data_referencia.strftime("%Y")
    dia = data_referencia.strftime("%d")
    mes = data_referencia.strftime("%m")

    return f"{ano}_{dia}_{mes}"


def gerar_nome_arquivo_final(instituicao, df_conciliado=None):
    instituicao = normalizar_nome_arquivo(instituicao)

    data_geracao = datetime.now().strftime("%Y_%d_%m")
    
    return f"conciliacao_{instituicao}_{data_geracao}.xlsx"


def preparar_arquivo_download(
    caminho_relatorio_origem,
    pasta_saida,
    instituicao,
    df_conciliado
):
    """
    Copia o relatório gerado pelo módulo 5 para um arquivo com nome final.
    """

    os.makedirs(pasta_saida, exist_ok=True)

    nome_arquivo_final = gerar_nome_arquivo_final(
        instituicao=instituicao,
        df_conciliado=df_conciliado
    )

    caminho_destino = os.path.join(
        pasta_saida,
        nome_arquivo_final
    )

    shutil.copyfile(
        caminho_relatorio_origem,
        caminho_destino
    )

    return {
        "nome_arquivo": nome_arquivo_final,
        "caminho_arquivo": caminho_destino,
    }