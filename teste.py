from core.fluxo_conciliacao import executar_fluxo_conciliacao


# ============================================================
# CONFIGURAÇÕES DO TESTE
# ============================================================

INSTITUICAO = "pagbank"

PASTA_SAIDA = r"C:\Users\yan.fernandes\Desktop\conciliador\saida_testes"

CAMINHO_ERP = (
    r"C:\Users\yan.fernandes\Documents\Conciliador PROD\pagbank"
    r"\Análise de Titulos de Cartão de Terceiros - SFR (14).csv"
)

CAMINHO_INSTITUICAO = (
    r"C:\Users\yan.fernandes\Documents\Conciliador PROD\pagbank"
    r"\PagBank_2026-04-17_17-24-39-detalhado.csv"
)


def exibir_resumo_resultado(resultado):
    df_erp = resultado["df_erp_padronizado"]
    df_instituicao = resultado["df_instituicao_padronizado"]
    df_conciliado = resultado["df_conciliado"]
    relatorio = resultado["relatorio"]
    download = resultado["download"]

    print("\n================ ERP PADRONIZADO ================")
    print(f"Linhas: {df_erp.shape[0]} | Colunas: {df_erp.shape[1]}")

    print("\n================ INSTITUICAO PADRONIZADA ================")
    print(f"Linhas: {df_instituicao.shape[0]} | Colunas: {df_instituicao.shape[1]}")

    print("\n================ RESULTADO DA CONCILIACAO ================")
    print(df_conciliado["status_conciliacao"].value_counts())

    print("\n================ RELATORIO FINAL ================")
    print(f"Arquivo base gerado: {relatorio['caminho_saida']}")
    print(f"Arquivo final download: {download['caminho_arquivo']}")
    print(f"Nome final: {download['nome_arquivo']}")
    print(f"Conciliados: {relatorio['qtd_conciliados']}")
    print(f"Nao conciliados: {relatorio['qtd_nao_conciliados']}")
    print(f"Valor liquido conciliado: {relatorio['valor_liquido_conciliado']}")
    print(f"Valor liquido nao conciliado: {relatorio['valor_liquido_nao_conciliado']}")
    
    
    validacao = resultado["validacao"]

    print("\n================ VALIDACAO DO FLUXO ================")

    if validacao["valido"]:
        print("Fluxo valido.")
    else:
        print("Fluxo invalido.")

    if validacao["erros"]:
        print("\nErros:")
        for erro in validacao["erros"]:
            print(f"- {erro}")

    if validacao["avisos"]:
        print("\nAvisos:")
        for aviso in validacao["avisos"]:
            print(f"- {aviso}")

    if not validacao["erros"] and not validacao["avisos"]:
        print("Nenhum erro ou aviso encontrado.")

def main():
    print("\n====================================================")
    print("INICIANDO TESTE DO FLUXO MODULAR")
    print("====================================================")
    print(f"Instituicao selecionada: {INSTITUICAO}")

    resultado = executar_fluxo_conciliacao(
        instituicao=INSTITUICAO,
        caminho_erp=CAMINHO_ERP,
        caminho_instituicao=CAMINHO_INSTITUICAO,
        pasta_saida=PASTA_SAIDA,
        salvar_intermediarios=True,
    )

    exibir_resumo_resultado(resultado)

    print("\n====================================================")
    print("TESTE FINALIZADO COM SUCESSO")
    print("====================================================")


if __name__ == "__main__":
    main()