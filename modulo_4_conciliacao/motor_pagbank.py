import pandas as pd
from rapidfuzz import fuzz


def normalizar_id(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "null", "<na>"]:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto.lower()


def calcular_similaridade(valor_erp, valor_instituicao):
    valor_erp = normalizar_id(valor_erp)
    valor_instituicao = normalizar_id(valor_instituicao)

    if valor_erp == "" or valor_instituicao == "":
        return 0

    if valor_erp == valor_instituicao:
        return 100

    return fuzz.ratio(valor_erp, valor_instituicao)


def gerar_status_pagbank(diferenca_dias, diferenca_valor, similaridade_autorizacao, similaridade_nsu):
    divergencias = []

    if diferenca_valor > 0:
        divergencias.append("Valor divergente")

    if diferenca_dias > 0:
        divergencias.append("Data divergente")

    if similaridade_autorizacao < 90:
        divergencias.append("Autorização divergente")

    if similaridade_nsu < 90:
        divergencias.append("NSU divergente")

    if not divergencias:
        return "Conciliado"

    return "Conciliado com: " + " | ".join(divergencias)


def calcular_score_pagbank(
    diferenca_dias,
    diferenca_valor,
    similaridade_autorizacao,
    similaridade_nsu,
    mesmo_cliente_pagseguro,
):
    bonus_pagseguro = -50 if mesmo_cliente_pagseguro else 0

    score = (
        diferenca_dias * 50
        + diferenca_valor * 200
        + (100 - similaridade_autorizacao)
        + (100 - similaridade_nsu)
        + bonus_pagseguro
    )

    return score


def preencher_dados_erp(df_instituicao, indice_instituicao, linha_erp):
    colunas_erp_saida = [
        "chave_erp",
        "numero_erp",
        "autorizacao_erp",
        "nsu_erp",
        "nsu_concentrador_erp",
        "data_emissao_erp",
        "data_correcao_erp",
        "valor_bruto_erp",
        "valor_liquido_erp",
        "parcela_erp",
        "total_parcelas_erp",
        "cliente_erp",
    ]

    for coluna in colunas_erp_saida:
        if coluna in linha_erp.index:
            df_instituicao.at[indice_instituicao, coluna] = linha_erp[coluna]


def conciliar_pagbank(
    df_instituicao,
    df_erp,
    tolerancia_dias=3,
    tolerancia_valor=0.30,
):
    df_instituicao = df_instituicao.copy()
    df_erp = df_erp.copy()

    df_erp["usada"] = False

    colunas_erp_saida = [
        "chave_erp",
        "numero_erp",
        "autorizacao_erp",
        "nsu_erp",
        "nsu_concentrador_erp",
        "data_emissao_erp",
        "data_correcao_erp",
        "valor_bruto_erp",
        "valor_liquido_erp",
        "parcela_erp",
        "total_parcelas_erp",
        "cliente_erp",
    ]

    for coluna in colunas_erp_saida:
        df_instituicao[coluna] = pd.NA

    df_instituicao["diferenca_dias"] = pd.NA
    df_instituicao["diferenca_valor"] = pd.NA
    df_instituicao["status_conciliacao"] = "Não conciliado"
    df_instituicao["pontuacao"] = 999.0

    for indice_instituicao, linha_instituicao in df_instituicao.iterrows():
        valor_pagbank = linha_instituicao["valor_liquido_instituicao"]
        data_pagbank = linha_instituicao["data_venda_instituicao"]
        autorizacao_pagbank = linha_instituicao["autorizacao_instituicao"]
        nsu_pagbank = linha_instituicao["nsu_instituicao"]

        if pd.isna(valor_pagbank) or pd.isna(data_pagbank):
            continue

        # Etapa 1: match perfeito PagSeguro
        mascara_pagseguro = (
            df_erp["cliente_erp"]
            .astype(str)
            .str.contains("pagseguro", case=False, na=False)
        )

        candidatos_perfeitos_pagseguro = df_erp[
            (~df_erp["usada"])
            & mascara_pagseguro
            & (df_erp["valor_liquido_erp"] == valor_pagbank)
            & (df_erp["data_emissao_erp"] == data_pagbank)
            & (df_erp["autorizacao_erp"].apply(normalizar_id) == normalizar_id(autorizacao_pagbank))
            & (df_erp["nsu_erp"].apply(normalizar_id) == normalizar_id(nsu_pagbank))
        ]

        if not candidatos_perfeitos_pagseguro.empty:
            indice_erp = candidatos_perfeitos_pagseguro.index[0]
            linha_erp = df_erp.loc[indice_erp]

            df_erp.at[indice_erp, "usada"] = True
            preencher_dados_erp(df_instituicao, indice_instituicao, linha_erp)

            df_instituicao.at[indice_instituicao, "diferenca_dias"] = 0
            df_instituicao.at[indice_instituicao, "diferenca_valor"] = 0
            df_instituicao.at[indice_instituicao, "status_conciliacao"] = "Conciliado"
            df_instituicao.at[indice_instituicao, "pontuacao"] = 0

            continue

        # Etapa 2: match perfeito geral
        candidatos_perfeitos = df_erp[
            (~df_erp["usada"])
            & (df_erp["valor_liquido_erp"] == valor_pagbank)
            & (df_erp["data_emissao_erp"] == data_pagbank)
            & (df_erp["autorizacao_erp"].apply(normalizar_id) == normalizar_id(autorizacao_pagbank))
            & (df_erp["nsu_erp"].apply(normalizar_id) == normalizar_id(nsu_pagbank))
        ]

        if not candidatos_perfeitos.empty:
            indice_erp = candidatos_perfeitos.index[0]
            linha_erp = df_erp.loc[indice_erp]

            df_erp.at[indice_erp, "usada"] = True
            preencher_dados_erp(df_instituicao, indice_instituicao, linha_erp)

            df_instituicao.at[indice_instituicao, "diferenca_dias"] = 0
            df_instituicao.at[indice_instituicao, "diferenca_valor"] = 0
            df_instituicao.at[indice_instituicao, "status_conciliacao"] = "Conciliado"
            df_instituicao.at[indice_instituicao, "pontuacao"] = 0

            continue

        # Etapa 3: candidatos por valor líquido e data
        candidatos = df_erp[
            (~df_erp["usada"])
            & (
                abs(df_erp["valor_liquido_erp"] - valor_pagbank)
                <= tolerancia_valor
            )
            & (
                abs((df_erp["data_emissao_erp"] - data_pagbank).dt.days)
                <= tolerancia_dias
            )
        ]

        melhor_candidato = None
        menor_score = float("inf")

        for indice_erp, linha_erp in candidatos.iterrows():
            diferenca_dias = abs(
                (linha_erp["data_emissao_erp"] - data_pagbank).days
            )

            diferenca_valor = abs(
                linha_erp["valor_liquido_erp"] - valor_pagbank
            )

            similaridade_autorizacao = calcular_similaridade(
                linha_erp["autorizacao_erp"],
                autorizacao_pagbank
            )

            similaridade_nsu = calcular_similaridade(
                linha_erp["nsu_erp"],
                nsu_pagbank
            )

            mesmo_cliente_pagseguro = (
                "pagseguro" in str(linha_erp.get("cliente_erp", "")).lower()
            )

            # Precisa ter pelo menos um identificador forte
            if similaridade_autorizacao < 85 and similaridade_nsu < 85:
                continue

            score = calcular_score_pagbank(
                diferenca_dias=diferenca_dias,
                diferenca_valor=diferenca_valor,
                similaridade_autorizacao=similaridade_autorizacao,
                similaridade_nsu=similaridade_nsu,
                mesmo_cliente_pagseguro=mesmo_cliente_pagseguro,
            )

            if score < menor_score:
                menor_score = score
                melhor_candidato = (
                    indice_erp,
                    linha_erp,
                    diferenca_dias,
                    diferenca_valor,
                    similaridade_autorizacao,
                    similaridade_nsu,
                )

        if melhor_candidato is None:
            continue

        (
            indice_erp,
            linha_erp,
            diferenca_dias,
            diferenca_valor,
            similaridade_autorizacao,
            similaridade_nsu,
        ) = melhor_candidato

        df_erp.at[indice_erp, "usada"] = True
        preencher_dados_erp(df_instituicao, indice_instituicao, linha_erp)

        status = gerar_status_pagbank(
            diferenca_dias=diferenca_dias,
            diferenca_valor=diferenca_valor,
            similaridade_autorizacao=similaridade_autorizacao,
            similaridade_nsu=similaridade_nsu,
        )

        df_instituicao.at[indice_instituicao, "diferenca_dias"] = diferenca_dias
        df_instituicao.at[indice_instituicao, "diferenca_valor"] = round(diferenca_valor, 2)
        df_instituicao.at[indice_instituicao, "status_conciliacao"] = status
        df_instituicao.at[indice_instituicao, "pontuacao"] = round(menor_score, 2)

    return df_instituicao, df_erp