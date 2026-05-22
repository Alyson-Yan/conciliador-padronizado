import pandas as pd
import os
import sys

CAMINHO_RAIZ = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

if CAMINHO_RAIZ not in sys.path:
    sys.path.insert(0, CAMINHO_RAIZ)
from modulo_2_upload.leitor_arquivos import carregar_arquivo_instituicao
from modulo_3_padronizacao.credishop_padronizador import padronizar_credishop


CAMINHO_CREDISHOP = (
    r"C:\Users\yan.fernandes\Documents\Conciliador PROD\conciliação credshop\creditos-efetuar-20250501-20250507.csv"
)

CAMINHO_SAIDA_DEBUG = (
    r"C:\Users\yan.fernandes\Desktop\conciliador\saida_testes"
    r"\credishop_debug_padronizada.xlsx"
)


def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 300)

    df_credishop_bruto = carregar_arquivo_instituicao(
        caminho_arquivo=CAMINHO_CREDISHOP,
        instituicao="credishop"
    )

    print("\n================ CREDISHOP BRUTA ================")
    print(f"Linhas: {df_credishop_bruto.shape[0]}")
    print(f"Colunas: {df_credishop_bruto.shape[1]}")
    print(df_credishop_bruto.head(10))

    df_credishop_padronizada = padronizar_credishop(df_credishop_bruto)

    print("\n================ CREDISHOP PADRONIZADA ================")
    print(f"Linhas: {df_credishop_padronizada.shape[0]}")
    print(f"Colunas: {df_credishop_padronizada.shape[1]}")

    print("\n================ COLUNAS PADRONIZADAS ================")
    for coluna in df_credishop_padronizada.columns:
        print(repr(coluna))

    print("\n================ TIPOS ================")
    print(df_credishop_padronizada.dtypes)

    print("\n================ NULOS ================")
    print(df_credishop_padronizada.isna().sum())

    print("\n================ AMOSTRA CAMPOS PRINCIPAIS ================")
    print(df_credishop_padronizada[[
        "instituicao",
        "data_pagamento_instituicao",
        "data_venda_instituicao",
        "data_vencimento_instituicao",
        "estabelecimento_instituicao",
        "tipo_lancamento_instituicao",
        "valor_bruto_instituicao",
        "valor_liquido_instituicao",
        "taxa_tarifa_instituicao",
        "nsu_instituicao",
        "codigo_venda_instituicao",
        "autorizacao_instituicao",
        "parcela_instituicao",
        "total_parcelas_instituicao",
        "maquininha_instituicao",
    ]].head(20))

    df_credishop_padronizada.to_excel(
        CAMINHO_SAIDA_DEBUG,
        index=False
    )

    print("\nPlanilha de debug gerada:")
    print(CAMINHO_SAIDA_DEBUG)




    print("\n================ LINHAS SEM DATA DE VENDA ================")

    linhas_sem_data_venda = df_credishop_padronizada[
        df_credishop_padronizada["data_venda_instituicao"].isna()
    ]

    print(linhas_sem_data_venda[[
        "data_pagamento_instituicao",
        "data_venda_instituicao",
        "estabelecimento_instituicao",
        "tipo_lancamento_instituicao",
        "valor_bruto_instituicao",
        "valor_liquido_instituicao",
        "taxa_tarifa_instituicao",
        "nsu_instituicao",
        "parcela_instituicao",
        "total_parcelas_instituicao",
        "maquininha_instituicao",
    ]])

if __name__ == "__main__":
    main()