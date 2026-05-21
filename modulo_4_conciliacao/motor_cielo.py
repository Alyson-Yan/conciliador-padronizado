from rapidfuzz import fuzz
import pandas as pd


def normalizar_comparacao(valor):
    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "null", "<na>"]:
        return ""

    if texto.endswith(".0"):
        texto = texto[:-2]

    return texto


def comparar_sem_zero_esquerda(valor_1, valor_2):
    texto_1 = normalizar_comparacao(valor_1).lstrip("0")
    texto_2 = normalizar_comparacao(valor_2).lstrip("0")

    return texto_1 == texto_2


def gerar_status_conciliacao(diferenca_valor, diferenca_dias, nsu_diferente, autorizacao_diferente):
    divergencias = []

    if diferenca_valor > 0:
        divergencias.append("Valor divergente")

    if diferenca_dias > 0:
        divergencias.append("Data divergente")

    if nsu_diferente:
        divergencias.append("NSU divergente")

    if autorizacao_diferente:
        divergencias.append("Autorização divergente")

    if not divergencias:
        return "Conciliado"

    return "Conciliado com: " + " | ".join(divergencias)


def conciliar_padronizado(
    df_instituicao,
    df_erp,
    tolerancia_dias=5,
    tolerancia_valor=0.20
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

        candidatos = df_erp[
            (~df_erp["usada"])
            & (
                abs(
                    (
                        df_erp["data_emissao_erp"]
                        - linha_instituicao["data_venda_instituicao"]
                    ).dt.days
                )
                <= tolerancia_dias
            )
            & (
                abs(
                    df_erp["valor_bruto_erp"]
                    - linha_instituicao["valor_bruto_instituicao"]
                )
                <= tolerancia_valor
            )
            & (df_erp["parcela_erp"] == linha_instituicao["parcela_instituicao"])
            & (df_erp["total_parcelas_erp"] == linha_instituicao["total_parcelas_instituicao"])
        ]

        melhor_candidato = None
        menor_pontuacao = float("inf")

        for indice_erp, linha_erp in candidatos.iterrows():
            diferenca_dias = abs(
                (
                    linha_erp["data_emissao_erp"]
                    - linha_instituicao["data_venda_instituicao"]
                ).days
            )

            diferenca_valor = abs(
                linha_erp["valor_bruto_erp"]
                - linha_instituicao["valor_bruto_instituicao"]
            )

            similaridade_autorizacao = fuzz.ratio(
                normalizar_comparacao(linha_erp["autorizacao_erp"]),
                normalizar_comparacao(linha_instituicao["autorizacao_instituicao"])
            )

            similaridade_nsu = fuzz.ratio(
                normalizar_comparacao(linha_erp["nsu_erp"]),
                normalizar_comparacao(linha_instituicao["nsu_instituicao"])
            )

            pontuacao = (
                diferenca_dias * 10
                + diferenca_valor * 100
                + (100 - similaridade_autorizacao)
                + (100 - similaridade_nsu)
            )

            if pontuacao < menor_pontuacao:
                menor_pontuacao = pontuacao
                melhor_candidato = (indice_erp, linha_erp, diferenca_dias, diferenca_valor)

        if melhor_candidato is None:
            continue

        indice_erp, linha_erp, diferenca_dias, diferenca_valor = melhor_candidato

        df_erp.at[indice_erp, "usada"] = True

        nsu_diferente = not comparar_sem_zero_esquerda(
            linha_erp["nsu_erp"],
            linha_instituicao["nsu_instituicao"]
        )

        autorizacao_diferente = (
            normalizar_comparacao(linha_erp["autorizacao_erp"])
            != normalizar_comparacao(linha_instituicao["autorizacao_instituicao"])
        )

        status = gerar_status_conciliacao(
            diferenca_valor=diferenca_valor,
            diferenca_dias=diferenca_dias,
            nsu_diferente=nsu_diferente,
            autorizacao_diferente=autorizacao_diferente,
        )

        for coluna in colunas_erp_saida:
            df_instituicao.at[indice_instituicao, coluna] = linha_erp[coluna]

        df_instituicao.at[indice_instituicao, "diferenca_dias"] = diferenca_dias
        df_instituicao.at[indice_instituicao, "diferenca_valor"] = round(diferenca_valor, 2)
        df_instituicao.at[indice_instituicao, "status_conciliacao"] = status
        df_instituicao.at[indice_instituicao, "pontuacao"] = round(menor_pontuacao, 2)

    return df_instituicao, df_erp