import pandas as pd
import os
import sys

CAMINHO_RAIZ = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if CAMINHO_RAIZ not in sys.path:
    sys.path.insert(0, CAMINHO_RAIZ)

from modulo_3_padronizacao.getnet_padronizador import padronizar_getnet


CAMINHO_GETNET = (
    r"C:\Users\yan.fernandes\Documents\Conciliador PROD\conciliação getnet"
    r"\Recebivel_Completos_9784485_20250101_20250131_17b71b847b834144add843c70f2feea1.xlsx"
)

CAMINHO_SAIDA_DEBUG = (
    r"C:\Users\yan.fernandes\Desktop\conciliador\saida_testes"
    r"\getnet_debug_padronizada.xlsx"
)


def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 300)

    df_getnet_bruto = pd.read_excel(
        CAMINHO_GETNET,
        sheet_name="Detalhado",
        header=None
    )

    print("\n================ GETNET BRUTO ================")
    print(f"Linhas: {df_getnet_bruto.shape[0]}")
    print(f"Colunas: {df_getnet_bruto.shape[1]}")
    print(df_getnet_bruto.head(15))

    df_getnet_padronizado = padronizar_getnet(df_getnet_bruto)

    print("\n================ GETNET PADRONIZADO ================")
    print(f"Linhas: {df_getnet_padronizado.shape[0]}")
    print(f"Colunas: {df_getnet_padronizado.shape[1]}")

    print("\n================ COLUNAS PADRONIZADAS ================")
    for coluna in df_getnet_padronizado.columns:
        print(repr(coluna))

    print("\n================ TIPOS ================")
    print(df_getnet_padronizado.dtypes)

    print("\n================ NULOS ================")
    print(df_getnet_padronizado.isna().sum())

    print("\n================ AMOSTRA CAMPOS PRINCIPAIS ================")
    colunas_principais = [
        "instituicao",
        "data_pagamento_instituicao",
        "data_venda_instituicao",
        "data_vencimento_instituicao",
        "estabelecimento_instituicao",
        "tipo_lancamento_instituicao",
        "valor_bruto_instituicao",
        "valor_liquido_instituicao",
        "taxa_tarifa_instituicao",
        "autorizacao_instituicao",
        "nsu_instituicao",
        "codigo_venda_instituicao",
        "parcela_instituicao",
        "total_parcelas_instituicao",
        "bandeira_instituicao",
        "modalidade_instituicao",
    ]

    colunas_existentes = [
        coluna for coluna in colunas_principais
        if coluna in df_getnet_padronizado.columns
    ]

    print(df_getnet_padronizado[colunas_existentes].head(30))

    print("\n================ TIPOS DE LANÇAMENTO ================")
    if "tipo_lancamento_instituicao" in df_getnet_padronizado.columns:
        print(
            df_getnet_padronizado["tipo_lancamento_instituicao"]
            .value_counts(dropna=False)
        )

    os.makedirs(os.path.dirname(CAMINHO_SAIDA_DEBUG), exist_ok=True)

    df_getnet_padronizado.to_excel(
        CAMINHO_SAIDA_DEBUG,
        index=False
    )

    print("\nPlanilha de debug gerada:")
    print(CAMINHO_SAIDA_DEBUG)


if __name__ == "__main__":
    main()