import pandas as pd
from rapidfuzz import process, fuzz


def encontrar_melhor_correspondencia_com_pontuacao(
    row,
    df_origem,
    coluna_erp
):

    correspondencias = process.extract(
        str(row["AUTORIZAÇÃO"]),
        df_origem[coluna_erp].astype(str),
        scorer=fuzz.ratio,
        limit=10
    )

    correspondencias_validas = [
        (texto, score, idx)
        for texto, score, idx in correspondencias
        if score >= 80
    ]

    if not correspondencias_validas:
        return pd.Series(
            [None, None, None, "Não Conciliado", 99]
        )

    melhor_resultado = None
    menor_pontuacao = float("inf")

    for melhor_correspondencia, _, _ in correspondencias_validas:

        filtro = df_origem[
            df_origem[coluna_erp] == melhor_correspondencia
        ]

        if filtro.empty:
            continue

        for _, linha_correspondente in filtro.iterrows():

            valor_erp = linha_correspondente["Valor"]
            data_erp = linha_correspondente["Emissão"]
            parcela_erp = linha_correspondente["Parcela"]
            total_parcelas_erp = linha_correspondente["Total_Parcelas"]

            status = ["Conciliado"]
            pontuacao = 0

            if abs(
                row["VALOR DA PARCELA"] - valor_erp
            ) > 0.10:

                status.append(
                    "Divergência de Valor"
                )
                pontuacao += 15

            if abs(
                (
                    row["DATA DA VENDA"] -
                    data_erp
                ).days
            ) > 1:

                status.append(
                    "Divergência de Data"
                )
                pontuacao += 5

            if row["PARCELA"] != parcela_erp:
                status.append(
                    "Divergência de Parcela"
                )
                pontuacao += 10

            if (
                row["TOTAL_PARCELAS"]
                !=
                total_parcelas_erp
            ):
                status.append(
                    "Divergência de Total de Parcelas"
                )
                pontuacao += 15

            if pontuacao < menor_pontuacao:

                menor_pontuacao = pontuacao

                melhor_resultado = (
                    linha_correspondente[coluna_erp],
                    linha_correspondente["Chave"],
                    valor_erp,
                    " com ".join(status)
                    if len(status) > 1
                    else status[0],
                    pontuacao
                )

    if melhor_resultado:
        return pd.Series(melhor_resultado)

    return pd.Series(
        [None, None, None, "Não Conciliado", 99]
    )


def marcar_duplicados_com_pior_score(
    df,
    chave_col="Chave ERP",
    status_col="Status",
    pontuacao_col="Pontuação"
):

    duplicadas = df[
        df.duplicated(
            subset=[chave_col],
            keep=False
        )
    ].copy()

    if duplicadas.empty:
        return df

    duplicadas_sorted = duplicadas.sort_values(
        pontuacao_col,
        ascending=True
    )

    duplicadas_marcadas = (
        duplicadas_sorted.duplicated(
            subset=[chave_col],
            keep="first"
        )
    )

    df.loc[
        duplicadas_sorted[
            duplicadas_marcadas
        ].index,
        status_col
    ] = "Valor Duplicado Menor Score"

    df.loc[
        duplicadas_sorted[
            duplicadas_marcadas
        ].index,
        pontuacao_col
    ] = 998

    return df