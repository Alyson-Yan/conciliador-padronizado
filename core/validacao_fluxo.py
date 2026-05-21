import os


COLUNAS_OBRIGATORIAS_ERP = [
    "agrupamento_erp",
    "chave_erp",
    "numero_erp",
    "parcela_erp",
    "total_parcelas_erp",
    "nsu_erp",
    "autorizacao_erp",
    "data_emissao_erp",
    "data_correcao_erp",
    "valor_bruto_erp",
    "valor_liquido_erp",
]


COLUNAS_OBRIGATORIAS_INSTITUICAO = [
    "instituicao",
    "valor_bruto_instituicao",
    "valor_liquido_instituicao",
    "taxa_tarifa_instituicao",
    "data_venda_instituicao",
    "data_vencimento_instituicao",
    "data_pagamento_instituicao",
    "autorizacao_instituicao",
    "nsu_instituicao",
    "codigo_venda_instituicao",
    "parcela_instituicao",
    "total_parcelas_instituicao",
]


COLUNAS_OBRIGATORIAS_CONCILIACAO = [
    "status_conciliacao",
    "pontuacao",
    "diferenca_dias",
    "diferenca_valor",
    "chave_erp",
    "valor_bruto_erp",
    "valor_liquido_erp",
    "valor_bruto_instituicao",
    "valor_liquido_instituicao",
]


def validar_colunas_obrigatorias(df, colunas_obrigatorias, nome):
    erros = []

    colunas_faltando = [
        coluna for coluna in colunas_obrigatorias
        if coluna not in df.columns
    ]

    if colunas_faltando:
        erros.append(
            f"{nome}: colunas faltando: {', '.join(colunas_faltando)}"
        )

    return erros


def validar_colunas_totalmente_vazias(df, colunas_obrigatorias, nome):
    avisos = []

    for coluna in colunas_obrigatorias:
        if coluna in df.columns and df[coluna].isna().all():
            avisos.append(
                f"{nome}: coluna totalmente vazia: {coluna}"
            )

    return avisos


def validar_dataframe_nao_vazio(df, nome):
    if df is None or df.empty:
        return [f"{nome}: dataframe vazio"]

    return []


def validar_arquivo_existe(caminho, nome):
    if not caminho or not os.path.exists(caminho):
        return [f"{nome}: arquivo não encontrado: {caminho}"]

    return []


def validar_status_conciliacao(df_conciliado):
    erros = []
    avisos = []

    if "status_conciliacao" not in df_conciliado.columns:
        erros.append("Conciliação: coluna status_conciliacao não encontrada")
        return erros, avisos

    total_status = df_conciliado["status_conciliacao"].value_counts(dropna=False)

    if total_status.empty:
        erros.append("Conciliação: nenhum status encontrado")

    if "Não conciliado" in total_status.index and len(total_status) == 1:
        avisos.append("Conciliação: todas as linhas ficaram como Não conciliado")

    return erros, avisos


def validar_resultado_fluxo(resultado):
    erros = []
    avisos = []

    df_erp = resultado.get("df_erp_padronizado")
    df_instituicao = resultado.get("df_instituicao_padronizado")
    df_conciliado = resultado.get("df_conciliado")

    relatorio = resultado.get("relatorio", {})
    download = resultado.get("download", {})

    erros += validar_dataframe_nao_vazio(df_erp, "ERP padronizado")
    erros += validar_dataframe_nao_vazio(df_instituicao, "Instituição padronizada")
    erros += validar_dataframe_nao_vazio(df_conciliado, "Conciliação")

    if df_erp is not None and not df_erp.empty:
        erros += validar_colunas_obrigatorias(
            df_erp,
            COLUNAS_OBRIGATORIAS_ERP,
            "ERP padronizado"
        )

        avisos += validar_colunas_totalmente_vazias(
            df_erp,
            COLUNAS_OBRIGATORIAS_ERP,
            "ERP padronizado"
        )

    if df_instituicao is not None and not df_instituicao.empty:
        erros += validar_colunas_obrigatorias(
            df_instituicao,
            COLUNAS_OBRIGATORIAS_INSTITUICAO,
            "Instituição padronizada"
        )

        avisos += validar_colunas_totalmente_vazias(
            df_instituicao,
            COLUNAS_OBRIGATORIAS_INSTITUICAO,
            "Instituição padronizada"
        )

    if df_conciliado is not None and not df_conciliado.empty:
        erros += validar_colunas_obrigatorias(
            df_conciliado,
            COLUNAS_OBRIGATORIAS_CONCILIACAO,
            "Conciliação"
        )

        status_erros, status_avisos = validar_status_conciliacao(df_conciliado)
        erros += status_erros
        avisos += status_avisos

    erros += validar_arquivo_existe(
        relatorio.get("caminho_saida"),
        "Relatório final"
    )

    erros += validar_arquivo_existe(
        download.get("caminho_arquivo"),
        "Arquivo de download"
    )

    return {
        "valido": len(erros) == 0,
        "erros": erros,
        "avisos": avisos,
    }


def exibir_resultado_validacao(validacao):
    print("\n================ VALIDAÇÃO DO FLUXO ================")

    if validacao["valido"]:
        print("Fluxo válido.")
    else:
        print("Fluxo inválido.")

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