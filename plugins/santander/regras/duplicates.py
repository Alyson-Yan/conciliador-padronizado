import pandas as pd
from rapidfuzz import process, fuzz


def conciliar_por_data_e_valores(row, df_erp_base):

    candidatos = filtrar_por_data(
        row,
        df_erp_base
    )

    candidatos = filtrar_por_valor_e_parcelas(
        row,
        candidatos
    )

    return montar_resultado(candidatos)


def filtrar_por_data(row, df):

    data_diferenca = (
        df["Emissão"] - row["DATA DA VENDA"]
    ).abs().dt.days

    return df[
        data_diferenca <= 5
    ]


def filtrar_por_valor_e_parcelas(row, candidatos):

    return candidatos[
        ((candidatos["Valor"] -
        row["VALOR DA PARCELA"]).abs() <= 0.20)

        &
        (candidatos["Parcela"] == row["PARCELA"])

        &
        (
            candidatos["Total_Parcelas"]
            ==
            row["TOTAL_PARCELAS"]
        )
    ]


def montar_resultado(candidatos):

    if not candidatos.empty:

        linha = candidatos.iloc[0]

        return pd.Series([
            linha["Autorização"],
            linha["Chave"],
            linha["Valor"],
            "Conciliado por Data e Valores",
            10
        ])

    return pd.Series([
        None,
        None,
        None,
        "Não Conciliado",
        99
    ])