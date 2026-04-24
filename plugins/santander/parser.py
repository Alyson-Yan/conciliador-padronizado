import pandas as pd


def limpar_layout_santander(df):
    df = df.iloc[6:].reset_index(drop=False)
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)
    return df


def normalizar_campos(df):
    df = df.filter(items=[
        "EC CENTRALIZADOR",
        "DATA DE VENCIMENTO",
        "TIPO DE LANÇAMENTO",
        "PARCELAS",
        "AUTORIZAÇÃO",
        "NÚMERO COMPROVANTE DE VENDA (NSU)",
        "DATA DA VENDA",
        "VALOR DA PARCELA",
        "VALOR LÍQUIDO"
    ])

    df["VALOR LÍQUIDO"] = pd.to_numeric(
        df["VALOR LÍQUIDO"], errors="coerce"
    )

    return df


def tratar_parcelas(df):
    df[["PARCELA", "TOTAL_PARCELAS"]] = (
        df["PARCELAS"].str.extract(r"(\d+)\s+de\s+(\d+)")
    )

    df["PARCELA"] = (
        pd.to_numeric(df["PARCELA"], errors="coerce")
        .fillna(1)
        .astype(int)
    )

    return df


def remover_lancamentos_indesejados(df):
    excluir = [
        "Cancelamento/Chargeback",
        "Aluguel/Tarifa",
        "Pagamento Realizado",
        "Saldo Anterior"
    ]

    return df[
        ~df["TIPO DE LANÇAMENTO"].isin(excluir)
    ]
    
def carregar_santander(caminho):

    df = pd.read_excel(caminho)

    df = limpar_layout_santander(df)
    df = normalizar_campos(df)
    df = tratar_parcelas(df)
    df = remover_lancamentos_indesejados(df)

    return df