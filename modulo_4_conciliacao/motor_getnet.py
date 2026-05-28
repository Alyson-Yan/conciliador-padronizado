import pandas as pd
from rapidfuzz import fuzz


CLIENTE_ESPERADO_GETNET = "Getnet Adquirencia E Servicos Para Meios de Pagamento S.a."


def normalizar_id(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "null", "<na>"]:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def inicializar_colunas_resultado(df_instituicao):
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


def eh_venda(linha):
    tipo = str(linha.get("tipo_lancamento_instituicao", "")).strip().lower()

    return tipo == "vendas"


def eh_cancelamento(linha):
    tipo = str(linha.get("tipo_lancamento_instituicao", "")).strip().lower()

    return "cancelamento" in tipo or "chargeback" in tipo


def eh_aluguel(linha):
    tipo = str(linha.get("tipo_lancamento_instituicao", "")).strip().lower()

    return "aluguel" in tipo or "tarifa" in tipo


def marcar_vendas_canceladas(df_instituicao):
    df = df_instituicao.copy()

    df["_valor_abs"] = pd.to_numeric(
        df["valor_bruto_instituicao"],
        errors="coerce"
    ).abs()

    df["_chave_cancelamento"] = (
        df["autorizacao_instituicao"].astype(str).str.strip()
        + "_"
        + df["_valor_abs"].astype(str)
    )

    cancelamentos = df[df.apply(eh_cancelamento, axis=1)].copy()

    if cancelamentos.empty:
        df = df.drop(columns=["_valor_abs", "_chave_cancelamento"], errors="ignore")
        return df

    chaves_cancelamento = set(cancelamentos["_chave_cancelamento"].dropna())

    mascara_venda_cancelada = (
        df.apply(eh_venda, axis=1)
        & df["_chave_cancelamento"].isin(chaves_cancelamento)
    )

    # No código antigo, a venda correspondente ao cancelamento era removida
    # da conciliação normal e somada aos cancelamentos.
    # Aqui mantemos a linha, mas mudamos o tipo para o relatório genérico
    # conseguir tratar como especial.
    df.loc[mascara_venda_cancelada, "tipo_lancamento_instituicao"] = "Cancelamento/Chargeback"

    df = df.drop(columns=["_valor_abs", "_chave_cancelamento"], errors="ignore")

    return df


def calcular_status_e_score(
    linha_instituicao,
    linha_erp,
    tolerancia_data_status=1,
    tolerancia_valor_status=0.10,
):
    data_venda = linha_instituicao["data_venda_instituicao"]
    data_erp = linha_erp["data_emissao_erp"]

    if pd.isna(data_erp) or pd.isna(data_venda):
        dias_dif = 999
    else:
        dias_dif = abs((data_erp - data_venda).days)

    valor_dif = abs(
        linha_erp["valor_bruto_erp"]
        - linha_instituicao["valor_bruto_instituicao"]
    )

    aut_getnet = normalizar_id(linha_instituicao["autorizacao_instituicao"])
    aut_erp = normalizar_id(linha_erp["autorizacao_erp"])

    nsu_getnet = normalizar_id(linha_instituicao["nsu_instituicao"])
    nsu_erp = normalizar_id(linha_erp["nsu_erp"])

    if aut_getnet == aut_erp or nsu_getnet == nsu_erp:
        sim_autorizacao = 100
        sim_nsu = 100
    else:
        sim_autorizacao = fuzz.ratio(aut_getnet, aut_erp)
        sim_nsu = fuzz.ratio(nsu_getnet, nsu_erp)

    pontuacao = (
        dias_dif * 100
        + valor_dif * 100
        + (200 - (sim_autorizacao + sim_nsu))
    )

    if (
        "cliente_erp" in linha_erp.index
        and linha_erp["cliente_erp"] != CLIENTE_ESPERADO_GETNET
    ):
        pontuacao += 101

    status_lista = ["Conciliado"]

    if valor_dif > tolerancia_valor_status:
        status_lista.append("Divergência de Valor")

    if dias_dif > tolerancia_data_status and dias_dif != 999:
        status_lista.append("Divergência de Data")
    elif dias_dif == 999:
        status_lista.append("Data Ausente")

    if (aut_getnet != aut_erp) and (nsu_getnet != nsu_erp):
        status_lista.append("Divergência de NSU/Autorização")
    elif aut_getnet != aut_erp:
        status_lista.append("Divergência de Autorização")
    elif nsu_getnet != nsu_erp:
        status_lista.append("Divergência de NSU")

    status_final = " e ".join(status_lista) if len(status_lista) > 1 else "Conciliado"

    return {
        "dias_dif": dias_dif,
        "valor_dif": valor_dif,
        "pontuacao": round(pontuacao, 2),
        "status": status_final,
    }


def selecionar_melhor_candidato(
    linha_instituicao,
    df_erp_base,
    tolerancia_dias=5,
    tolerancia_valor=0.20,
):
    data_venda = linha_instituicao["data_venda_instituicao"]
    valor_bruto = linha_instituicao["valor_bruto_instituicao"]
    parcela = linha_instituicao["parcela_instituicao"]
    total_parcelas = linha_instituicao["total_parcelas_instituicao"]

    if pd.isna(data_venda) or pd.isna(valor_bruto):
        return None

    candidatos = df_erp_base[
        (
            abs((df_erp_base["data_emissao_erp"] - data_venda).dt.days)
            <= tolerancia_dias
        )
        & (
            abs(df_erp_base["valor_bruto_erp"] - valor_bruto)
            <= tolerancia_valor
        )
        & (df_erp_base["parcela_erp"] == parcela)
        & (df_erp_base["total_parcelas_erp"] == total_parcelas)
    ].copy()

    if candidatos.empty:
        return None

    melhor_resultado = None
    menor_pontuacao = float("inf")

    for indice_erp, linha_erp in candidatos.iterrows():
        avaliacao = calcular_status_e_score(
            linha_instituicao=linha_instituicao,
            linha_erp=linha_erp,
        )

        if avaliacao["pontuacao"] < menor_pontuacao:
            menor_pontuacao = avaliacao["pontuacao"]
            melhor_resultado = {
                "indice_erp": indice_erp,
                "linha_erp": linha_erp,
                "status": avaliacao["status"],
                "pontuacao": avaliacao["pontuacao"],
                "diferenca_dias": avaliacao["dias_dif"],
                "diferenca_valor": avaliacao["valor_dif"],
            }

    return melhor_resultado


def aplicar_resultado_conciliacao(
    df_instituicao,
    indice_instituicao,
    resultado,
):
    linha_erp = resultado["linha_erp"]

    preencher_dados_erp(
        df_instituicao=df_instituicao,
        indice_instituicao=indice_instituicao,
        linha_erp=linha_erp,
    )

    df_instituicao.at[indice_instituicao, "status_conciliacao"] = resultado["status"]
    df_instituicao.at[indice_instituicao, "pontuacao"] = resultado["pontuacao"]
    df_instituicao.at[indice_instituicao, "diferenca_dias"] = resultado["diferenca_dias"]
    df_instituicao.at[indice_instituicao, "diferenca_valor"] = round(
        resultado["diferenca_valor"],
        2
    )


def marcar_duplicados_com_pior_score(
    df_instituicao,
    chave_col="chave_erp",
    status_col="status_conciliacao",
    pontuacao_col="pontuacao",
):
    mascara_conciliada = (
        df_instituicao[pontuacao_col].notna()
        & (df_instituicao[pontuacao_col] != 999)
        & df_instituicao[chave_col].notna()
    )

    duplicadas = df_instituicao[
        mascara_conciliada
        & df_instituicao.duplicated(subset=[chave_col], keep=False)
    ].copy()

    if duplicadas.empty:
        return df_instituicao

    duplicadas_sorted = duplicadas.sort_values(pontuacao_col, ascending=True)
    duplicadas_marcadas = duplicadas_sorted.duplicated(
        subset=[chave_col],
        keep="first"
    )

    indices_piores = duplicadas_sorted[duplicadas_marcadas].index

    df_instituicao.loc[indices_piores, status_col] = "Valor Duplicado Menor Score"
    df_instituicao.loc[indices_piores, pontuacao_col] = 998

    return df_instituicao


def obter_chaves_utilizadas(df_instituicao):
    mascara_utilizada = (
        df_instituicao["chave_erp"].notna()
        & (df_instituicao["pontuacao"] != 999)
        & (df_instituicao["pontuacao"] != 998)
        & df_instituicao["status_conciliacao"].astype(str).str.startswith("Conciliado", na=False)
    )

    return set(
        df_instituicao.loc[mascara_utilizada, "chave_erp"]
        .astype(str)
        .str.strip()
        .dropna()
    )


def conciliar_rodada(
    df_instituicao,
    df_erp,
    indices_para_conciliar,
    tolerancia_dias,
    tolerancia_valor,
    bloquear_erp_usado=True,
):
    for indice_instituicao in indices_para_conciliar:
        linha_instituicao = df_instituicao.loc[indice_instituicao]

        if not eh_venda(linha_instituicao):
            continue

        if bloquear_erp_usado:
            df_erp_base = df_erp[~df_erp["usada"]]
        else:
            df_erp_base = df_erp

        resultado = selecionar_melhor_candidato(
            linha_instituicao=linha_instituicao,
            df_erp_base=df_erp_base,
            tolerancia_dias=tolerancia_dias,
            tolerancia_valor=tolerancia_valor,
        )

        if resultado is None:
            continue

        indice_erp = resultado["indice_erp"]

        if bloquear_erp_usado:
            df_erp.at[indice_erp, "usada"] = True

        aplicar_resultado_conciliacao(
            df_instituicao=df_instituicao,
            indice_instituicao=indice_instituicao,
            resultado=resultado,
        )


def conciliar_getnet(
    df_instituicao,
    df_erp,
    tolerancia_dias=5,
    tolerancia_valor=0.20,
):
    df_instituicao = df_instituicao.copy()
    df_erp = df_erp.copy()

    df_instituicao = marcar_vendas_canceladas(df_instituicao)

    df_erp["chave_erp"] = pd.to_numeric(
        df_erp["chave_erp"],
        errors="coerce"
    ).astype("string")

    df_erp["usada"] = False

    inicializar_colunas_resultado(df_instituicao)

    # =========================
    # 1ª rodada: fiel ao original
    # tolerância padrão: 5 dias e R$ 0,20
    # =========================

    indices_vendas = df_instituicao[
        df_instituicao.apply(eh_venda, axis=1)
    ].index

    conciliar_rodada(
        df_instituicao=df_instituicao,
        df_erp=df_erp,
        indices_para_conciliar=indices_vendas,
        tolerancia_dias=tolerancia_dias,
        tolerancia_valor=tolerancia_valor,
        bloquear_erp_usado=False,
    )

    # =========================
    # Duplicados: mantém menor score
    # =========================

    df_instituicao = marcar_duplicados_com_pior_score(df_instituicao)

    # Recalcula ERP usado considerando apenas os conciliados bons.
    chaves_utilizadas = obter_chaves_utilizadas(df_instituicao)

    df_erp["usada"] = (
        df_erp["chave_erp"]
        .astype(str)
        .str.strip()
        .isin(chaves_utilizadas)
    )

    # =========================
    # 2ª rodada: igual ao original
    # tenta encontrar possível ERP para os não conciliados,
    # mas NÃO transforma essas linhas em conciliadas.
    #
    # No código antigo, essa etapa preenchia dados auxiliares
    # na aba de não conciliados, mas os títulos continuavam
    # como "Não conciliado".
    # =========================

    indices_segunda_rodada = df_instituicao[
        df_instituicao.apply(eh_venda, axis=1)
        & (
            (df_instituicao["pontuacao"] == 999)
            | (df_instituicao["pontuacao"] == 998)
        )
    ].index

    for indice_instituicao in indices_segunda_rodada:
        linha_instituicao = df_instituicao.loc[indice_instituicao]

        resultado = selecionar_melhor_candidato(
            linha_instituicao=linha_instituicao,
            df_erp_base=df_erp[~df_erp["usada"]],
            tolerancia_dias=30,
            tolerancia_valor=100000.00,
        )

        if resultado is None:
            continue

        preencher_dados_erp(
            df_instituicao=df_instituicao,
            indice_instituicao=indice_instituicao,
            linha_erp=resultado["linha_erp"],
        )

        df_instituicao.at[indice_instituicao, "diferenca_dias"] = resultado[
            "diferenca_dias"
        ]

        df_instituicao.at[indice_instituicao, "diferenca_valor"] = round(
            resultado["diferenca_valor"],
            2
        )

        # Ponto principal:
        # mantém como Não conciliado para não ir para a aba Conciliados.
        df_instituicao.at[
            indice_instituicao,
            "status_conciliacao"
        ] = "Não conciliado"

        df_instituicao.at[indice_instituicao, "pontuacao"] = 999

    return df_instituicao, df_erp
