import pandas as pd


COLUNAS_INSTITUICAO_PADRAO = [
    "instituicao",

    # Datas principais
    "data_pagamento_instituicao",
    "data_lancamento_instituicao",
    "data_venda_instituicao",
    "hora_venda_instituicao",
    "data_vencimento_instituicao",

    # Identificação da venda
    "estabelecimento_instituicao",
    "tipo_lancamento_instituicao",
    "forma_pagamento_instituicao",
    "bandeira_instituicao",
    "modalidade_instituicao",
    "tipo_captura_instituicao",
    "canal_venda_instituicao",
    "status_pagamento_instituicao",


    # Valores
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

    # Códigos de conciliação
    "autorizacao_instituicao",
    "nsu_instituicao",
    "codigo_venda_instituicao",
    "tid_instituicao",
    "id_pix_instituicao",
    "txid_instituicao",
    "codigo_chave_ur_instituicao",

    # Cartão / pedido / lote
    "numero_cartao_instituicao",
    "origem_cartao_instituicao",
    "numero_lote_instituicao",

    # Parcelamento
    "parcela_instituicao",
    "total_parcelas_instituicao",

    # Máquina / referência
    "maquininha_instituicao",
    "total_dias_cobrados_instituicao",
    "quantidade_pinpads_instituicao",

    # Dados bancários
    "banco_instituicao",
    "agencia_instituicao",
    "conta_instituicao",

    # Negociação
]


MAPEAMENTO_CIELO = {
    # Datas principais
    "Data de pagamento": "data_pagamento_instituicao",
    "Data do lan�amento": "data_lancamento_instituicao",
    "Data do lançamento": "data_lancamento_instituicao",
    "Data da venda": "data_venda_instituicao",
    "Hora da venda": "hora_venda_instituicao",
    "Data prevista de pagamento": "data_vencimento_instituicao",

    # Identificação da venda
    "Estabelecimento": "estabelecimento_instituicao",
    "Tipo de lan�amento": "tipo_lancamento_instituicao",
    "Tipo de lançamento": "tipo_lancamento_instituicao",
    "Forma de pagamento": "forma_pagamento_instituicao",
    "Bandeira": "bandeira_instituicao",
    "Modalidade": "modalidade_instituicao",
    "Tipo de captura": "tipo_captura_instituicao",
    "Canal da venda": "canal_venda_instituicao",
    "Status de pagamento": "status_pagamento_instituicao",

    # Valores
    "Valor bruto": "valor_bruto_instituicao",
    "Taxa/tarifa": "taxa_tarifa_instituicao",
    "Valor l�quido": "valor_liquido_instituicao",
    "Valor líquido": "valor_liquido_instituicao",
    "Taxa total (%)": "taxa_total_percentual_instituicao",
    "Taxa administrativa (MDR) (%)": "taxa_administrativa_percentual_instituicao",
    "Taxa de recebimento autom�tico (%)": "taxa_recebimento_automatico_percentual_instituicao",
    "Taxa de recebimento automático (%)": "taxa_recebimento_automatico_percentual_instituicao",
    "Valor da taxa administrativa (MDR)": "valor_taxa_administrativa_instituicao",
    "Valor da taxa de recebimento autom�tico": "valor_taxa_recebimento_automatico_instituicao",
    "Valor da taxa de recebimento automático": "valor_taxa_recebimento_automatico_instituicao",
    "Valor do saque": "valor_saque_instituicao",
    "Valor do troco": "valor_troco_instituicao",
    "Valor total da transa��o": "valor_total_transacao_instituicao",
    "Valor total da transação": "valor_total_transacao_instituicao",

    # Códigos de conciliação
    "C�digo da autoriza��o": "autorizacao_instituicao",
    "Código da autorização": "autorizacao_instituicao",
    "NSU/DOC": "nsu_instituicao",
    "C�digo da venda": "codigo_venda_instituicao",
    "Código da venda": "codigo_venda_instituicao",
    "TID": "tid_instituicao",
    "ID Pix": "id_pix_instituicao",
    "TxID": "txid_instituicao",
    "C�digo da chave UR": "codigo_chave_ur_instituicao",
    "Código da chave UR": "codigo_chave_ur_instituicao",

    # Cartão / pedido / lote
    "N�mero do cart�o": "numero_cartao_instituicao",
    "Número do cartão": "numero_cartao_instituicao",
    "Origem do cart�o": "origem_cartao_instituicao",
    "Origem do cartão": "origem_cartao_instituicao",
    "N�mero do lote": "numero_lote_instituicao",
    "Número do lote": "numero_lote_instituicao",

    # Parcelamento
    "N�mero da parcela": "parcela_instituicao",
    "Número da parcela": "parcela_instituicao",
    "Quantidade total de parcelas": "total_parcelas_instituicao",

    # Máquina / referência
    "N�mero da m�quina": "maquininha_instituicao",
    "Número da máquina": "maquininha_instituicao",
    "Total de dias cobrados": "total_dias_cobrados_instituicao",
    "Quantidade de Pinpads": "quantidade_pinpads_instituicao",

    # Dados bancários
    "Banco": "banco_instituicao",
    "Ag�ncia": "agencia_instituicao",
    "Agência": "agencia_instituicao",
    "Conta": "conta_instituicao",
}


def normalizar_coluna(coluna):
    return str(coluna).strip()


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


def converter_percentual(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none", "null", "<na>"]:
        return pd.NA

    texto = texto.replace("%", "").replace(" ", "")

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


def preparar_cabecalho_cielo(df_cielo_bruto):
    df = df_cielo_bruto.copy()

    # Linha 10 no Excel = índice 9 no pandas
    df = df.iloc[9:].reset_index(drop=True)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    df.columns = [normalizar_coluna(coluna) for coluna in df.columns]

    return df


def padronizar_cielo(df_cielo_bruto):
    df = preparar_cabecalho_cielo(df_cielo_bruto)

    df = df.rename(columns=MAPEAMENTO_CIELO)

    for coluna in COLUNAS_INSTITUICAO_PADRAO:
        if coluna not in df.columns:
            df[coluna] = pd.NA

    df["instituicao"] = "cielo"

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

    colunas_percentuais = [
        "taxa_total_percentual_instituicao",
        "taxa_administrativa_percentual_instituicao",
        "taxa_recebimento_automatico_percentual_instituicao",
    ]

    for coluna in colunas_percentuais:
        df[coluna] = df[coluna].apply(converter_percentual)

    colunas_datas = [
        "data_pagamento_instituicao",
        "data_lancamento_instituicao",
        "data_venda_instituicao",
        "data_vencimento_instituicao",
    ]

    for coluna in colunas_datas:
        df[coluna] = df[coluna].apply(converter_data)

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

    df["parcela_instituicao"] = (
        pd.to_numeric(df["parcela_instituicao"], errors="coerce")
        .fillna(1)
        .astype(int)
    )

    df["total_parcelas_instituicao"] = (
        pd.to_numeric(df["total_parcelas_instituicao"], errors="coerce")
        .fillna(1)
        .astype(int)
    )

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