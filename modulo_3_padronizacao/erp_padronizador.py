import re
import pandas as pd


COLUNAS_ERP_PADRAO = [
    "agrupamento_erp",
    "chave_criacao_erp",
    "chave_erp",
    "cliente_erp",
    "nome_cliente_erp",
    "numero_erp",
    "parcela_erp",
    "total_parcelas_erp",
    "nsu_erp",
    "nsu_concentrador_erp",
    "autorizacao_erp",
    "data_emissao_erp",
    "data_correcao_erp",
    "valor_bruto_erp",
    "valor_liquido_erp",
    "taxa_erp",
    "tipo_lancamento_erp",
    "carteira_erp",
    "caracterizacao_venda_erp",
]


MAPEAMENTO_ERP = {
    "1o. Agrupamento": "agrupamento_erp",
    "Ch Criação": "chave_criacao_erp",
    "Ch Criacao": "chave_criacao_erp",
    "Chave": "chave_erp",
    "Pessoa do Título": "cliente_erp",
    "Pessoa do Titulo": "cliente_erp",
    "Nome do Cliente": "nome_cliente_erp",
    "Numero": "numero_erp",
    "Número": "numero_erp",
    "NSU": "nsu_erp",
    "NSU Concentrador": "nsu_concentrador_erp",
    "Autorização": "autorizacao_erp",
    "Autorizacao": "autorizacao_erp",
    "Emissão": "data_emissao_erp",
    "Emissao": "data_emissao_erp",
    "Correção": "data_correcao_erp",
    "Correcao": "data_correcao_erp",
    "Valor": "valor_bruto_erp",
    "Vr Corrigido": "valor_liquido_erp",
    "Taxa": "taxa_erp",
    "Tipo": "tipo_lancamento_erp",
    "Carteira": "carteira_erp",
    "Caracterização da Venda": "caracterizacao_venda_erp",
    "Caracterizacao da Venda": "caracterizacao_venda_erp",
}


def normalizar_nome_coluna(nome):
    return str(nome).strip()


def converter_valor_monetario(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none", "null"]:
        return pd.NA

    texto = (
        texto
        .replace("R$", "")
        .replace(" ", "")
    )

    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return pd.NA


def converter_data(valor):
    if pd.isna(valor):
        return pd.NaT

    return pd.to_datetime(valor, dayfirst=True, errors="coerce").normalize()


def limpar_texto(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "null", "<na>"]:
        return ""

    return texto


def limpar_identificador(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "null", "<na>"]:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def extrair_parcelas(numero):
    if pd.isna(numero):
        return 1, 1

    texto = str(numero).strip()

    padrao = re.search(r"-(\d+)\s*/\s*(\d+)", texto)

    if not padrao:
        padrao = re.search(r"(\d+)\s*/\s*(\d+)", texto)

    if not padrao:
        return 1, 1

    parcela = int(padrao.group(1))
    total = int(padrao.group(2))

    if parcela <= 0:
        parcela = 1

    if total <= 0:
        total = 1

    return parcela, total


def remover_sufixo_parcela(numero):
    if pd.isna(numero):
        return ""

    texto = str(numero).strip()
    texto = re.sub(r"-(\d+)\s*/\s*(\d+)", "", texto)

    return texto.strip()


def padronizar_erp(df_erp_bruto):
    df = df_erp_bruto.copy()

    df.columns = [normalizar_nome_coluna(coluna) for coluna in df.columns]

    df = df.rename(columns=MAPEAMENTO_ERP)

    for coluna in COLUNAS_ERP_PADRAO:
        if coluna not in df.columns:
            df[coluna] = pd.NA

    if "numero_erp" in df.columns:
        parcelas = df["numero_erp"].apply(extrair_parcelas)

        df["parcela_erp"] = parcelas.apply(lambda item: item[0])
        df["total_parcelas_erp"] = parcelas.apply(lambda item: item[1])
        df["numero_erp"] = df["numero_erp"].apply(remover_sufixo_parcela)

    colunas_texto = [
        "agrupamento_erp",
        "cliente_erp",
        "nome_cliente_erp",
        "numero_erp",
        "tipo_lancamento_erp",
        "carteira_erp",
        "caracterizacao_venda_erp",
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].apply(limpar_texto)

    colunas_identificadores = [
        "chave_criacao_erp",
        "chave_erp",
        "nsu_erp",
        "nsu_concentrador_erp",
        "autorizacao_erp",
    ]

    for coluna in colunas_identificadores:
        df[coluna] = df[coluna].apply(limpar_identificador)

    colunas_datas = [
        "data_emissao_erp",
        "data_correcao_erp",
    ]

    for coluna in colunas_datas:
        df[coluna] = df[coluna].apply(converter_data)

    colunas_valores = [
        "valor_bruto_erp",
        "valor_liquido_erp",
        "taxa_erp",
    ]

    for coluna in colunas_valores:
        df[coluna] = df[coluna].apply(converter_valor_monetario)

    df["parcela_erp"] = (
        pd.to_numeric(df["parcela_erp"], errors="coerce")
        .fillna(1)
        .astype(int)
    )

    df["total_parcelas_erp"] = (
        pd.to_numeric(df["total_parcelas_erp"], errors="coerce")
        .fillna(1)
        .astype(int)
    )

    df = df[COLUNAS_ERP_PADRAO]

    return df

