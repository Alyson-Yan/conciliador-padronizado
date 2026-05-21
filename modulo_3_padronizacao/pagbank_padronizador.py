import re
import pandas as pd


COLUNAS_INSTITUICAO_PADRAO = [
    "instituicao",

    "data_pagamento_instituicao",
    "data_lancamento_instituicao",
    "data_venda_instituicao",
    "hora_venda_instituicao",
    "data_vencimento_instituicao",

    "estabelecimento_instituicao",
    "tipo_lancamento_instituicao",
    "forma_pagamento_instituicao",
    "bandeira_instituicao",
    "modalidade_instituicao",
    "tipo_captura_instituicao",
    "canal_venda_instituicao",
    "status_pagamento_instituicao",

    "valor_bruto_instituicao",
    "valor_liquido_instituicao",
    "taxa_tarifa_instituicao",
    "taxa_total_percentual_instituicao",
    "taxa_administrativa_percentual_instituicao",
    "taxa_recebimento_automatico_percentual_instituicao",
    "valor_taxa_administrativa_instituicao",
    "valor_taxa_recebimento_automatico_instituicao",
    "valor_saque_instituicao",
    "valor_troco_instituicao",
    "valor_total_transacao_instituicao",

    "autorizacao_instituicao",
    "nsu_instituicao",
    "codigo_venda_instituicao",
    "tid_instituicao",
    "id_pix_instituicao",
    "txid_instituicao",
    "codigo_chave_ur_instituicao",

    "numero_cartao_instituicao",
    "origem_cartao_instituicao",
    "numero_lote_instituicao",

    "parcela_instituicao",
    "total_parcelas_instituicao",

    "maquininha_instituicao",
    "total_dias_cobrados_instituicao",
    "quantidade_pinpads_instituicao",

    "banco_instituicao",
    "agencia_instituicao",
    "conta_instituicao",
]


MAPEAMENTO_PAGBANK = {
    "Código da Transação": "codigo_transacao_instituicao",
    "Data da Transação": "data_venda_instituicao",
    "Data prevista de liberação": "data_vencimento_instituicao",
    "Bandeira": "bandeira_instituicao",
    "Forma de Pagamento": "forma_pagamento_instituicao",
    "Parcela": "parcela_original_instituicao",
    "Valor Bruto": "valor_bruto_instituicao",
    "Valor Taxa": "taxa_tarifa_instituicao",
    "Valor Líquido": "valor_liquido_instituicao",
    "Código NSU": "codigo_venda_instituicao",
    "Código de Autorização": "autorizacao_instituicao",
    "Identificação da Maquininha": "maquininha_instituicao",
    "Código da Venda": "nsu_instituicao",
    "Status": "status_pagamento_instituicao",
}


def converter_valor_monetario(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none", "null", "<na>"]:
        return pd.NA

    texto = texto.replace("R$", "").replace(" ", "")

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


def extrair_parcelas_pagbank(valor):
    if pd.isna(valor):
        return 1, 1

    texto = str(valor).lower().strip()

    match_barra = re.search(r"(\d+)\s*/\s*(\d+)", texto)

    if match_barra:
        return int(match_barra.group(1)), int(match_barra.group(2))

    match_x = re.search(r"(\d+)\s*x", texto)

    if match_x:
        total = int(match_x.group(1))
        return 1, total

    return 1, 1


def padronizar_pagbank(df_pagbank_bruto):
    df = df_pagbank_bruto.copy()

    df = df.rename(columns=MAPEAMENTO_PAGBANK)

    for coluna in COLUNAS_INSTITUICAO_PADRAO:
        if coluna not in df.columns:
            df[coluna] = pd.NA

    df["instituicao"] = "pagbank"

    df["data_venda_instituicao"] = df["data_venda_instituicao"].apply(converter_data)
    df["data_vencimento_instituicao"] = df["data_vencimento_instituicao"].apply(converter_data)

    # Na PagBank, a data de recebimento mais próxima no arquivo antigo é a prevista de liberação.
    df["data_pagamento_instituicao"] = df["data_vencimento_instituicao"]

    colunas_valores = [
        "valor_bruto_instituicao",
        "valor_liquido_instituicao",
        "taxa_tarifa_instituicao",
        "valor_taxa_administrativa_instituicao",
        "valor_taxa_recebimento_automatico_instituicao",
        "valor_saque_instituicao",
        "valor_troco_instituicao",
        "valor_total_transacao_instituicao",
    ]

    for coluna in colunas_valores:
        df[coluna] = df[coluna].apply(converter_valor_monetario)

    colunas_identificadores = [
        "autorizacao_instituicao",
        "nsu_instituicao",
        "codigo_venda_instituicao",
        "tid_instituicao",
        "id_pix_instituicao",
        "txid_instituicao",
        "codigo_chave_ur_instituicao",
        "numero_cartao_instituicao",
        "numero_lote_instituicao",
        "maquininha_instituicao",
        "banco_instituicao",
        "agencia_instituicao",
        "conta_instituicao",
    ]

    for coluna in colunas_identificadores:
        df[coluna] = df[coluna].apply(limpar_identificador)

    colunas_texto = [
        "estabelecimento_instituicao",
        "tipo_lancamento_instituicao",
        "forma_pagamento_instituicao",
        "bandeira_instituicao",
        "modalidade_instituicao",
        "tipo_captura_instituicao",
        "canal_venda_instituicao",
        "status_pagamento_instituicao",
        "origem_cartao_instituicao",
        "hora_venda_instituicao",
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].apply(limpar_texto)

    parcelas = df["parcela_original_instituicao"].apply(
        lambda valor: pd.Series(extrair_parcelas_pagbank(valor))
    )

    df["parcela_instituicao"] = parcelas[0].fillna(1).astype(int)
    df["total_parcelas_instituicao"] = parcelas[1].fillna(1).astype(int)

    df["total_dias_cobrados_instituicao"] = (
        pd.to_numeric(df["total_dias_cobrados_instituicao"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    df["quantidade_pinpads_instituicao"] = (
        pd.to_numeric(df["quantidade_pinpads_instituicao"], errors="coerce")
        .fillna(0)
        .astype(int)
    )

    df = df[COLUNAS_INSTITUICAO_PADRAO]

    return df