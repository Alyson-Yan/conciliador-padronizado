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


COLUNAS_ORIGINAIS_GetNet = [
    "EC CENTRALIZADOR",
    "DATA DE VENCIMENTO",
    "TIPO DE LANÇAMENTO",
    "PARCELAS",
    "AUTORIZAÇÃO",
    "NÚMERO COMPROVANTE DE VENDA (NSU)",
    "DATA DA VENDA",
    "VALOR DA PARCELA",
    "VALOR LÍQUIDO",
    "BANDEIRA / MODALIDADE",
]


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


def converter_data(valor):
    if pd.isna(valor):
        return pd.NaT

    data = pd.to_datetime(valor, dayfirst=True, errors="coerce")

    if pd.isna(data):
        return pd.NaT

    return data.normalize()


def converter_valor(valor):
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


def preparar_arquivo_GetNet(df_GetNet_bruto):
    df = df_GetNet_bruto.copy()

    # Procura dinamicamente a linha do cabeçalho real.
    # No GetNet, essa linha contém "EC CENTRALIZADOR".
    indice_cabecalho = None

    for indice, linha in df.iterrows():
        valores_linha = linha.astype(str).str.strip().tolist()

        if "EC CENTRALIZADOR" in valores_linha:
            indice_cabecalho = indice
            break

    if indice_cabecalho is None:
        raise ValueError("Cabeçalho do GetNet não encontrado: EC CENTRALIZADOR")

    # Define a linha encontrada como cabeçalho
    df.columns = df.iloc[indice_cabecalho]

    # Remove tudo até a linha do cabeçalho
    df = df.iloc[indice_cabecalho + 1:].reset_index(drop=True)

    # Remove colunas totalmente vazias
    df = df.dropna(axis=1, how="all")

    # Remove linhas totalmente vazias
    df = df.dropna(axis=0, how="all")

    # Remove colunas duplicadas, se existirem
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # Mantém apenas as colunas necessárias
    colunas_existentes = [
        coluna for coluna in COLUNAS_ORIGINAIS_GetNet
        if coluna in df.columns
    ]

    colunas_faltando = [
        coluna for coluna in COLUNAS_ORIGINAIS_GetNet
        if coluna not in df.columns
    ]

    if colunas_faltando:
        print("\nATENCAO: colunas GetNet faltando:")
        for coluna in colunas_faltando:
            print(f"- {coluna}")

    df = df[colunas_existentes].copy()

    return df


def extrair_parcelas(valor):
    if pd.isna(valor):
        return 1, 1

    texto = str(valor).strip()

    if texto == "" or texto.lower() in ["nan", "none", "null", "<na>"]:
        return 1, 1

    parcelas = pd.Series(texto).str.extract(r"(\d+)\s+de\s+(\d+)")

    parcela_atual = pd.to_numeric(parcelas.iloc[0, 0], errors="coerce")
    total_parcelas = pd.to_numeric(parcelas.iloc[0, 1], errors="coerce")

    if pd.isna(parcela_atual):
        parcela_atual = 1

    if pd.isna(total_parcelas):
        total_parcelas = 1

    return int(parcela_atual), int(total_parcelas)


def separar_bandeira_modalidade(valor):
    texto = limpar_texto(valor)

    if texto == "":
        return "", ""

    # Mantém simples por enquanto:
    # o campo inteiro fica como bandeira/modalidade para não perder informação.
    return texto, texto


def padronizar_GetNet(df_GetNet_bruto):
    df = preparar_arquivo_GetNet(df_GetNet_bruto)

    # Remove linhas que não representam venda nem evento financeiro útil.
    # "Total Recebido" aparece como linha de subtotal e vem com tipo vazio.
    df["TIPO DE LANÇAMENTO"] = df["TIPO DE LANÇAMENTO"].apply(limpar_texto)

    df = df[
        df["TIPO DE LANÇAMENTO"].notna()
        & (df["TIPO DE LANÇAMENTO"] != "")
        & (df["TIPO DE LANÇAMENTO"] != "Saldo Anterior")
        & (df["TIPO DE LANÇAMENTO"] != "Pagamento Realizado")
    ].copy()

    # Mantemos "Vendas", "Cancelamento/Chargeback" e "Aluguel/Tarifa".
    # O motor vai conciliar apenas vendas.
    # O relatório pode jogar cancelamento/aluguel em abas especiais.

    df_padronizado = pd.DataFrame(index=df.index)

    df_padronizado["instituicao"] = "GetNet"

    df_padronizado["data_pagamento_instituicao"] = df["DATA DE VENCIMENTO"].apply(converter_data)
    df_padronizado["data_lancamento_instituicao"] = pd.NaT
    df_padronizado["data_venda_instituicao"] = df["DATA DA VENDA"].apply(converter_data)
    df_padronizado["hora_venda_instituicao"] = ""
    df_padronizado["data_vencimento_instituicao"] = df["DATA DE VENCIMENTO"].apply(converter_data)

    df_padronizado["estabelecimento_instituicao"] = df["EC CENTRALIZADOR"].apply(limpar_texto)
    df_padronizado["tipo_lancamento_instituicao"] = df["TIPO DE LANÇAMENTO"].apply(limpar_texto)
    df_padronizado["forma_pagamento_instituicao"] = ""
    df_padronizado["tipo_captura_instituicao"] = ""
    df_padronizado["canal_venda_instituicao"] = ""
    df_padronizado["status_pagamento_instituicao"] = df["TIPO DE LANÇAMENTO"].apply(limpar_texto)

    bandeira_modalidade = df["BANDEIRA / MODALIDADE"].apply(
        lambda valor: pd.Series(separar_bandeira_modalidade(valor))
    )

    df_padronizado["bandeira_instituicao"] = bandeira_modalidade[0]
    df_padronizado["modalidade_instituicao"] = bandeira_modalidade[1]

    df_padronizado["valor_bruto_instituicao"] = df["VALOR DA PARCELA"].apply(converter_valor)
    df_padronizado["valor_liquido_instituicao"] = df["VALOR LÍQUIDO"].apply(converter_valor)

    df_padronizado["taxa_tarifa_instituicao"] = (
        df_padronizado["valor_bruto_instituicao"]
        - df_padronizado["valor_liquido_instituicao"]
    )

    df_padronizado["taxa_total_percentual_instituicao"] = pd.NA
    df_padronizado["taxa_administrativa_percentual_instituicao"] = pd.NA
    df_padronizado["taxa_recebimento_automatico_percentual_instituicao"] = pd.NA
    df_padronizado["valor_taxa_administrativa_instituicao"] = pd.NA
    df_padronizado["valor_taxa_recebimento_automatico_instituicao"] = pd.NA
    df_padronizado["valor_saque_instituicao"] = pd.NA
    df_padronizado["valor_troco_instituicao"] = pd.NA
    df_padronizado["valor_total_transacao_instituicao"] = df_padronizado["valor_bruto_instituicao"]

    df_padronizado["autorizacao_instituicao"] = df["AUTORIZAÇÃO"].apply(limpar_identificador)
    df_padronizado["nsu_instituicao"] = df["NÚMERO COMPROVANTE DE VENDA (NSU)"].apply(limpar_identificador)
    df_padronizado["codigo_venda_instituicao"] = df_padronizado["nsu_instituicao"]

    df_padronizado["tid_instituicao"] = ""
    df_padronizado["id_pix_instituicao"] = ""
    df_padronizado["txid_instituicao"] = ""
    df_padronizado["codigo_chave_ur_instituicao"] = ""

    df_padronizado["numero_cartao_instituicao"] = ""
    df_padronizado["origem_cartao_instituicao"] = ""
    df_padronizado["numero_lote_instituicao"] = ""

    parcelas = df["PARCELAS"].apply(
        lambda valor: pd.Series(extrair_parcelas(valor))
    )

    df_padronizado["parcela_instituicao"] = parcelas[0].fillna(1).astype(int)
    df_padronizado["total_parcelas_instituicao"] = parcelas[1].fillna(1).astype(int)

    df_padronizado["maquininha_instituicao"] = df["EC CENTRALIZADOR"].apply(limpar_identificador)
    df_padronizado["total_dias_cobrados_instituicao"] = 0
    df_padronizado["quantidade_pinpads_instituicao"] = 0

    df_padronizado["banco_instituicao"] = ""
    df_padronizado["agencia_instituicao"] = ""
    df_padronizado["conta_instituicao"] = ""

    for coluna in COLUNAS_INSTITUICAO_PADRAO:
        if coluna not in df_padronizado.columns:
            df_padronizado[coluna] = pd.NA

    df_padronizado = df_padronizado[COLUNAS_INSTITUICAO_PADRAO]

    return df_padronizado