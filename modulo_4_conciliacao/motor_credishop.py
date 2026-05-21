import pandas as pd
from rapidfuzz import fuzz


def normalizar_id(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "null", "<na>"]:
        return ""

    texto = texto.replace(",", ".")

    try:
        numero = float(texto)
        if numero.is_integer():
            texto = str(int(numero))
    except ValueError:
        pass

    return texto.lstrip("0")


def inicializar_colunas_resultado(df_instituicao):
    colunas_erp_saida = [
        "nsu_erp",
        "chave_erp",
        "valor_bruto_erp",
        "data_emissao_erp",
        "parcela_erp",
        "total_parcelas_erp",
        "cliente_erp",
    ]

    for coluna in colunas_erp_saida:
        df_instituicao[coluna] = pd.NA

    # Mantém também as colunas extras do padrão atual,
    # mesmo que o original antigo não usasse todas.
    colunas_extras_padrao = [
        "numero_erp",
        "autorizacao_erp",
        "nsu_concentrador_erp",
        "data_correcao_erp",
        "valor_liquido_erp",
    ]

    for coluna in colunas_extras_padrao:
        df_instituicao[coluna] = pd.NA

    df_instituicao["diferenca_dias"] = pd.NA
    df_instituicao["diferenca_valor"] = pd.NA
    df_instituicao["status_conciliacao"] = "Não conciliado"
    df_instituicao["pontuacao"] = 999.0


def preencher_dados_erp(df_instituicao, indice_instituicao, linha_erp):
    mapa_colunas = {
        "nsu_erp": "nsu_erp",
        "chave_erp": "chave_erp",
        "valor_bruto_erp": "valor_bruto_erp",
        "data_emissao_erp": "data_emissao_erp",
        "parcela_erp": "parcela_erp",
        "total_parcelas_erp": "total_parcelas_erp",
        "cliente_erp": "cliente_erp",

        # Extras do padrão novo
        "numero_erp": "numero_erp",
        "autorizacao_erp": "autorizacao_erp",
        "nsu_concentrador_erp": "nsu_concentrador_erp",
        "data_correcao_erp": "data_correcao_erp",
        "valor_liquido_erp": "valor_liquido_erp",
    }

    for coluna_destino, coluna_origem in mapa_colunas.items():
        if coluna_origem in linha_erp.index:
            df_instituicao.at[indice_instituicao, coluna_destino] = linha_erp[coluna_origem]


def montar_status_original(
    linha_instituicao,
    linha_erp,
    dias_dif,
    valor_dif,
):
    status_lista = ["Conciliado"]

    if valor_dif != 0:
        status_lista.append("Divergência de Valor")

    if dias_dif != 0:
        status_lista.append("Divergência de Data")

    if linha_instituicao["parcela_instituicao"] != linha_erp["parcela_erp"]:
        status_lista.append("Divergência de Parcela")

    if linha_instituicao["total_parcelas_instituicao"] != linha_erp["total_parcelas_erp"]:
        status_lista.append("Divergência de Total de Parcelas")

    nsu_credishop = normalizar_id(linha_instituicao["nsu_instituicao"])
    nsu_erp = normalizar_id(linha_erp["nsu_erp"])

    if nsu_credishop != nsu_erp:
        status_lista.append("Divergência de NSU")

    if len(status_lista) > 1:
        return " e ".join(status_lista)

    return "Conciliado"


def conciliar_credishop(
    df_instituicao,
    df_erp,
    tolerancia_dias=5,
    tolerancia_valor=0.20,
):
    df_instituicao = df_instituicao.copy()
    df_erp = df_erp.copy()

    df_erp["chave_erp"] = pd.to_numeric(
        df_erp["chave_erp"],
        errors="coerce"
    ).astype("string")

    df_erp["usada"] = False

    inicializar_colunas_resultado(df_instituicao)

    total = len(df_instituicao)

    for i, linha_instituicao in df_instituicao.iterrows():
        nsu_credishop = linha_instituicao["nsu_instituicao"]

        # Igual ao original:
        # se não tiver NSU/DOC, não tenta conciliar.
        if pd.isna(nsu_credishop) or str(nsu_credishop).strip() == "":
            continue

        data_venda = linha_instituicao["data_venda_instituicao"]
        valor_bruto = linha_instituicao["valor_bruto_instituicao"]
        parcela_atual = linha_instituicao["parcela_instituicao"]
        total_parcelas = linha_instituicao["total_parcelas_instituicao"]

        if pd.isna(data_venda) or pd.isna(valor_bruto):
            continue

        # Mesmo filtro base do código original:
        # data, valor bruto, parcela atual e total de parcelas.
        candidatos = df_erp[
            (~df_erp["usada"])
            & (
                abs((df_erp["data_emissao_erp"] - data_venda).dt.days)
                <= tolerancia_dias
            )
            & (
                abs(df_erp["valor_bruto_erp"] - valor_bruto)
                <= tolerancia_valor
            )
            & (df_erp["parcela_erp"] == parcela_atual)
            & (df_erp["total_parcelas_erp"] == total_parcelas)
        ]

        melhor = None
        menor_pontuacao = float("inf")
        melhor_status = "Não conciliado"
        melhor_dif_dias = None
        melhor_dif_valor = None

        for _, linha_erp in candidatos.iterrows():
            dias_dif = abs(
                (linha_erp["data_emissao_erp"] - data_venda).days
            )

            valor_dif = abs(
                linha_erp["valor_bruto_erp"] - valor_bruto
            )

            sim_nsu = fuzz.ratio(
                str(linha_erp["nsu_erp"]),
                str(nsu_credishop)
            )

            # Mesmo controle do código original
            dias_dif = min(dias_dif, 30) if pd.notna(dias_dif) else 30
            valor_dif = min(valor_dif, 1000) if pd.notna(valor_dif) else 1000
            sim_nsu = sim_nsu if pd.notna(sim_nsu) else 0

            pontuacao = (
                dias_dif * 10
                + valor_dif * 100
                + (100 - sim_nsu)
            )

            pontuacao = min(pontuacao, 999)

            # Mesma penalidade do original:
            # se achou candidato mas Pessoa do Título não for Credishop,
            # joga a pontuação para baixo da lista.
            if (
                "cliente_erp" in linha_erp.index
                and linha_erp["cliente_erp"] != "Credishop"
            ):
                pontuacao += 101

            status_final = montar_status_original(
                linha_instituicao=linha_instituicao,
                linha_erp=linha_erp,
                dias_dif=dias_dif,
                valor_dif=valor_dif,
            )

            if pontuacao < menor_pontuacao:
                menor_pontuacao = pontuacao
                melhor = linha_erp
                melhor_status = status_final
                melhor_dif_dias = dias_dif
                melhor_dif_valor = valor_dif

        if melhor is not None:
            idx_erp = df_erp.index[
                df_erp["chave_erp"] == melhor["chave_erp"]
            ].tolist()

            if idx_erp:
                df_erp.at[idx_erp[0], "usada"] = True

            preencher_dados_erp(
                df_instituicao=df_instituicao,
                indice_instituicao=i,
                linha_erp=melhor,
            )

            df_instituicao.at[i, "status_conciliacao"] = melhor_status
            df_instituicao.at[i, "pontuacao"] = round(menor_pontuacao, 0)
            df_instituicao.at[i, "diferenca_dias"] = melhor_dif_dias
            df_instituicao.at[i, "diferenca_valor"] = melhor_dif_valor

        else:
            # Igual ao original:
            # se não achou candidato, mantém Não conciliado e dados ERP vazios.
            df_instituicao.at[i, "status_conciliacao"] = "Não conciliado"
            df_instituicao.at[i, "pontuacao"] = 999

    return df_instituicao, df_erp