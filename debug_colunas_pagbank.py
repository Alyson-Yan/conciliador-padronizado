import pandas as pd

from modulo_3_padronizacao.erp_padronizador import padronizar_erp
from modulo_3_padronizacao.pagbank_padronizador import padronizar_pagbank


CAMINHO_ERP = (
    r"C:\Users\yan.fernandes\Documents\Conciliador PROD\pagbank"
    r"\Análise de Titulos de Cartão de Terceiros - SFR (14).csv"
)

CAMINHO_PAGBANK = (
    r"C:\Users\yan.fernandes\Documents\Conciliador PROD\pagbank"
    r"\PagBank_2026-04-17_17-24-39-detalhado.csv"
)


def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 300)

    df_erp_bruto = pd.read_csv(
        CAMINHO_ERP,
        sep=";",
        encoding="latin1"
    )

    df_pagbank_bruto = pd.read_csv(
        CAMINHO_PAGBANK,
        sep=";",
        encoding="utf-8-sig"
    )

    df_erp = padronizar_erp(df_erp_bruto)
    df_pagbank = padronizar_pagbank(df_pagbank_bruto)

    print("\n================ PAGBANK PADRONIZADA ================")
    print(df_pagbank[[
        "valor_liquido_instituicao",
        "valor_bruto_instituicao",
        "data_venda_instituicao",
        "data_vencimento_instituicao",
        "autorizacao_instituicao",
        "nsu_instituicao",
        "codigo_venda_instituicao",
        "parcela_instituicao",
        "total_parcelas_instituicao",
    ]])

    print("\n================ ERP CAMPOS PRINCIPAIS ================")
    print(df_erp[[
        "valor_liquido_erp",
        "valor_bruto_erp",
        "data_emissao_erp",
        "data_correcao_erp",
        "autorizacao_erp",
        "nsu_erp",
        "nsu_concentrador_erp",
        "parcela_erp",
        "total_parcelas_erp",
        "cliente_erp",
        "chave_erp",
    ]].head(50))

    print("\n================ BUSCA DE CANDIDATOS POR VALOR LIQUIDO E DATA ================")

    for indice, linha_pagbank in df_pagbank.iterrows():
        valor = linha_pagbank["valor_liquido_instituicao"]
        data = linha_pagbank["data_venda_instituicao"]

        candidatos = df_erp[
            (abs(df_erp["valor_liquido_erp"] - valor) <= 0.30)
            &
            (abs((df_erp["data_emissao_erp"] - data).dt.days) <= 3)
        ].copy()

        print("\n----------------------------------------------------")
        print(f"PAGBANK linha {indice}")
        print(f"Valor liquido PagBank: {valor}")
        print(f"Data venda PagBank: {data}")
        print(f"Autorizacao PagBank: {linha_pagbank['autorizacao_instituicao']}")
        print(f"NSU PagBank: {linha_pagbank['nsu_instituicao']}")
        print(f"Codigo venda PagBank: {linha_pagbank['codigo_venda_instituicao']}")
        print(f"Candidatos ERP encontrados: {len(candidatos)}")

        if not candidatos.empty:
            print(candidatos[[
                "valor_liquido_erp",
                "valor_bruto_erp",
                "data_emissao_erp",
                "autorizacao_erp",
                "nsu_erp",
                "nsu_concentrador_erp",
                "parcela_erp",
                "total_parcelas_erp",
                "cliente_erp",
                "chave_erp",
            ]].head(10))


if __name__ == "__main__":
    main()